from postgresql_integration_test.log import logger
import atexit
import tempfile
import shutil
import psutil
import time
import getpass
import os
import signal
import subprocess
import psycopg2
from datetime import datetime

from postgresql_integration_test import settings
from postgresql_integration_test.version import __version__
from postgresql_integration_test.settings import ConfigFile
from postgresql_integration_test.settings import ConfigInstance


class PostgreSQL:
    def __init__(self, **kwargs):
        logger.debug(f"postgresql-integration-test {__version__}")

        self.child_process = None
        self.terminate_signal = signal.SIGTERM
        self.owner_pid = None
        self.user = getpass.getuser()
        self.base_dir = tempfile.mkdtemp()
        self.config = ConfigFile(base_dir=self.base_dir)

        if "config_file" in kwargs:
            self.config.general.config_file = kwargs["config_file"]

        self.config = settings.parse_config(self.config, kwargs)
        logger.setlevel(self.config.general.log_level)

        atexit.register(self.stop)

    def __del__(self):
        logger.debug(f"Cleaning up temp dir {self.config.dirs.base_dir}")
        # Sleep for a 1/2 sec to allow mysql to shut down
        print("LOL")
        while self.child_process is not None:
            time.sleep(0.5)
        if self.config.general.cleanup_dirs and os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)

    def close(self):
        self.__del__()

    def run(self):
        if self.child_process:
            logger.error("Error, database already running!")
            return False

        self.owner_pid = os.getpid()

        logger.debug("Creating application directories")
        os.mkdir(self.config.dirs.tmp_dir)
        os.chmod(self.config.dirs.tmp_dir, 0o700)
        os.mkdir(self.config.dirs.etc_dir)
        os.mkdir(self.config.dirs.data_dir)

        try:
            logger.debug("Initializing PostgreSQL w/initdb")
            pgsql_command_line = [
                shutil.which("initdb"),
                f"-g",
                f"-D {os.path.join(self.config.dirs.data_dir)}",
                f"-U {self.user}",
            ]
            logger.debug(f"PG_CTL_INITDB_CMD: {pgsql_command_line}")
            subprocess.Popen(
                pgsql_command_line, stdout=subprocess.STDERR, stderr=subprocess.STDOUT
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize PostgreSQL: {exc}")

        try:
            logger.debug("Creating Database")
            pgsql_command_line = [
                shutil.which("createdb"),
                f"-U {self.user}",
                self.database.name,
            ]
            subprocess.Popen(
                pgsql_command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
        except Exception as exc:
            raise RuntimeError(f"Failed create database: {self.database.name}")

        try:
            logger.debug(
                f"Starting PostgreSQL at {os.path.join(self.config.dirs.data_dir)}"
            )
            pgsql_command_line = [
                shutil.which("postgres"),
                f"-D {os.path.join(self.config.dirs.data_dir)}",
            ]
            logger.debug(f"PG_CTL_START_CMD: {pgsql_command_line}")
            self.child_process = subprocess.Popen(
                pgsql_command_line, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT
            )
            time.sleep(300)
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize PostgreSQL: {exc}")
        else:
            try:
                self.wait_booting()
            except Exception:
                self.stop()
                raise

        instance_config = ConfigInstance(
            {
                "host": self.config.database.host,
                "port": self.config.database.port,
                "username": self.config.database.username,
            }
        )

        return instance_config

    def connect(self):
        return

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
                if (
                    datetime.now() - killed_at
                ).seconds > self.config.general.timeout_stop:
                    self.child_process.kill()
                    raise RuntimeError("Failed to shutdown PostgreSQL (timeout)")

                time.sleep(0.5)
        except OSError:
            pass

        self.child_process = None

    def wait_booting(self):
        exec_at = datetime.now()
        while True:
            if self.child_process.poll() is not None:
                raise RuntimeError(
                    "Failed to launch PostgreSQL binary - child process is null"
                )

            if self.is_server_available():
                break

            if (datetime.now() - exec_at).seconds > self.config.general.timeout_start:
                raise RuntimeError("Failed to launch PostgreSQL binary (timeout)")

            time.sleep(0.5)

    def is_server_available(self):
        return "postgres" in (i.name() for i in psutil.process_iter())
