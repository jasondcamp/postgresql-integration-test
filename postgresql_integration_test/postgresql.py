import atexit
import tempfile
import shutil
import time
import getpass
import os
import signal
import subprocess
from datetime import datetime
import psycopg2
#import mysql.connector

#from mysqld_integration_test.log import logger
#from mysqld_integration_test import settings
#from mysqld_integration_test.settings import ConfigFile
#from mysqld_integration_test.settings import ConfigInstance
#from mysqld_integration_test.version import __version__


class PostgreSQL:
    def __init__(self, **kwargs):
        logger.debug(f"mysqd-integration-test {__version__}")

        self.child_process = None
        self.terminate_signal = signal.SIGTERM
        self.owner_pid = None
        self.current_user = getpass.getuser()
        self.base_dir = tempfile.mkdtemp()
        self.config = ConfigFile(base_dir=self.base_dir)

        if 'config_file' in kwargs:
            self.config.general.config_file = kwargs['config_file']

        self.config = settings.parse_config(self.config, kwargs)
        logger.setlevel(self.config.general.log_level)

        atexit.register(self.stop)

    def __del__(self):
        logger.debug(f"Cleaning up temp dir {self.config.dirs.base_dir}")
        # Sleep for a 1/2 sec to allow mysql to shut down
        while self.child_process is not None:
            time.sleep(0.5)
        if self.config.general.cleanup_dirs and os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)

    def close(self):
        self.__del__()

    def run(self):
        if self.child_process:
            logger.error("Error, database already running!")
            return False  # already started

        # Set the owner pid
        self.owner_pid = os.getpid()

        # Build the mysql base fileset
        # Make base directories
        logger.debug("Creating application directories")
        os.mkdir(self.config.dirs.tmp_dir)
        os.chmod(self.config.dirs.tmp_dir, 0o700)
        os.mkdir(self.config.dirs.etc_dir)
        os.mkdir(self.config.dirs.data_dir)

        # Write my.cnf
        logger.debug("Writing my.cnf")
        self.write_mycnf()

        # Display version data
        logger.debug(f"VERSION: {self.config.version.variant} {self.config.version.major} {self.config.version.minor}")

        # Initialize database files
        if self.config.version.variant == "mariadb" and self.config.version.major >= 10:
            logger.debug("Initializing databases with mysql_install_db")
            mysql_install_db_command_line = [self.config.database.mysql_install_db_binary,
                                             f"--defaults-file={os.path.join(self.config.dirs.etc_dir, 'my.cnf')}",
                                             f"--datadir={self.config.dirs.data_dir}"]
            logger.debug(f"MYSQL_INSTALL_DB_CMD: {mysql_install_db_command_line}")
            process = subprocess.Popen(mysql_install_db_command_line,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            (output, error) = process.communicate()
            logger.debug(f"MySQL initialization error: {output} {error}")

        elif self.config.version.variant == "mysql" and self.config.version.major >= 8:
            logger.debug("Initializing databases with mysqld")
            mysqld_command_line = [self.config.database.mysqld_binary,
                                   "--initialize-insecure",
                                   f"--datadir={self.config.dirs.data_dir}",
                                   f"--log-error={os.path.join(self.config.dirs.tmp_dir, 'errors.log')}"]
            logger.debug(f"MYSQL_INIT_DB_CMD: {mysqld_command_line}")
            process = subprocess.Popen(mysqld_command_line,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            (output, error) = process.communicate()
            logger.debug(f"MySQL initialization error: {output} {error}")

        # Start up the database
        try:
            logger.debug("Starting mysqld")
            mysqld_command_line = [self.config.database.mysqld_binary,
                                   f"--defaults-file={os.path.join(self.config.dirs.etc_dir, 'my.cnf')}",
                                   f"--user={self.current_user}"]
            logger.debug(f"MYSQL_START_CMD: {mysqld_command_line}")
            self.child_process = subprocess.Popen(mysqld_command_line,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.STDOUT)
        except Exception as exc:
            raise RuntimeError(f"Failed to start mysqld: {exc}")
        else:
            try:
                self.wait_booting()
            except Exception:
                self.stop()
                raise

        # MariaDB 10 requires that you log in as the user that is running the mysql instance and reset the root pw
        # Set password
        # Get the current user
        if self.config.version.variant == "mariadb" and self.config.version.major >= 10:
            logger.debug("Detected MariaDB >= 10: Resetting password")
            self.reset_mysqld_password(self.current_user)
        elif self.config.version.variant == "mysql" and self.config.version.major >= 8:
            logger.debug("Detected MySQL >= 8: Resetting password")
            self.reset_mysqld_password('root')

        # create test database
        self.create_test_database()

        # Return specifics the user can use to connect to the test instance
        instance_config = ConfigInstance({
                'host': self.config.database.host,
                'port': self.config.database.port,
                'username': self.config.database.username,
                'password': self.config.database.password,
                'socket_file': self.config.database.socket_file})

        return instance_config

    def reset_mysqld_password(self, current_user):
        cnx = mysql.connector.connect(user=current_user,
                                      unix_socket=self.config.database.socket_file,
                                      host=self.config.database.host,
                                      port=self.config.database.port)
        cursor = cnx.cursor()
        cursor.execute(f"ALTER USER '{self.config.database.username}'@'localhost' IDENTIFIED BY '{self.config.database.password}';")  # noqa: E501
        cursor.execute("FLUSH PRIVILEGES;")
        cnx.commit()
        cursor.close()
        cnx.close()

    def create_test_database(self):
        cnx = mysql.connector.connect(user=self.config.database.username,
                                      password=self.config.database.password,
                                      host=self.config.database.host,
                                      port=self.config.database.port)
        cursor = cnx.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS test')
        cnx.commit()
        cursor.close()
        cnx.close()

    def stop(self, _signal=signal.SIGTERM):
        self.terminate(_signal)

    def terminate(self, _signal=None):
        if self.child_process is None:
            return  # not started

        if self.owner_pid != os.getpid():
            return  # could not stop in child process

        if _signal is None:
            _signal = self.terminate_signal

        try:
            logger.debug("Stopping server")
            self.child_process.send_signal(_signal)
            killed_at = datetime.now()
            while self.child_process.poll() is None:
                if (datetime.now() - killed_at).seconds > self.config.general.timeout_stop:
                    self.child_process.kill()
                    raise RuntimeError("Failed to shutdown mysql (timeout)")

                time.sleep(0.5)
        except OSError:
            pass

        self.child_process = None

    def write_mycnf(self):
        with open(os.path.join(self.config.dirs.etc_dir, 'my.cnf'), 'wt', encoding='utf-8') as my_cnf:
            my_cnf.write("[mysqld]" + "\n")
            my_cnf.write(f"bind-address={self.config.database.host}" + "\n")
            my_cnf.write(f"port={self.config.database.port}" + "\n")
            my_cnf.write(f"datadir={self.config.dirs.data_dir}" + "\n")
            my_cnf.write(f"tmpdir={self.config.dirs.tmp_dir}" + "\n")
            my_cnf.write(f"socket={self.config.database.socket_file}" + "\n")
            my_cnf.write(f"pid-file={self.config.database.pid_file}" + "\n")
            my_cnf.write(f"secure-file-priv={self.config.dirs.tmp_dir}" + "\n")

    def wait_booting(self):
        exec_at = datetime.now()
        while True:
            if self.child_process.poll() is not None:
                raise RuntimeError("Failed to launch mysql binary - child process is null")

            if self.is_server_available():
                break

            if (datetime.now() - exec_at).seconds > self.config.general.timeout_start:
                raise RuntimeError("Failed to launch mysql binary (timeout)")

            time.sleep(0.5)

    def is_server_available(self):
        return os.path.exists(self.config.database.pid_file)
