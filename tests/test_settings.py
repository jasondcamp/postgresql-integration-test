import pytest
import functools
from mysqld_integration_test import Mysqld


@pytest.fixture
def mysqld_connect(autouse=True):
    return Mysqld()


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


# Make sure config options exists and check some defaults
@pytest.mark.settings_test
def test_settings_test(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config') is not None


@pytest.mark.settings_test
def test_dirs_basedir_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.dirs.base_dir') is not None


@pytest.mark.settings_test
def test_dirs_datadir_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.dirs.data_dir') is not None


@pytest.mark.settings_test
def test_dirs_etcdir_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.dirs.etc_dir') is not None


@pytest.mark.settings_test
def test_dirs_tmpdir_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.dirs.tmp_dir') is not None


@pytest.mark.settings_test
def test_database_host_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.database.host') is not None


@pytest.mark.settings_test
def test_database_port_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.database.port') is not None


@pytest.mark.settings_test
def test_datbase_username_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.database.username') is not None


@pytest.mark.settings_test
def test_database_password_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.database.password') is not None


@pytest.mark.settings_test
def test_database_socketfile_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.database.socket_file') is not None


@pytest.mark.settings_test
def test_database_pidfile_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.database.pid_file') is not None


@pytest.mark.settings_test
def test_database_mysqldbinary_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.database.mysqld_binary') is not None


@pytest.mark.settings_test
def test_database_mysqlinstalldbbinary_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.database.mysql_install_db_binary') is not None


@pytest.mark.settings_test
def test_general_timeoutstart_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.general.timeout_start') is not None


@pytest.mark.settings_test
def test_general_timeoutstop_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.general.timeout_stop') is not None


@pytest.mark.settings_test
def test_general_loglevel_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.general.log_level') is not None


@pytest.mark.settings_test
def test_general_configfile_exists(mysqld_connect):
    assert rgetattr(mysqld_connect, 'config.general.config_file') is not None


# Test that a config option that we know doesn't exist does not exist
@pytest.mark.settings_test
def test_general_faketest_notexists(mysqld_connect):
    with pytest.raises(AttributeError):
        _ = rgetattr(mysqld_connect, 'config.general.faketest') is None


# Test a config option passed in as an argument works
@pytest.mark.settings_test
def test_arg_config_option_exists():
    mysqld = Mysqld(port='8888')
    assert mysqld.config.database.port == '8888'


# Test that a config file option works
@pytest.mark.settings_test
def test_config_file_option_exists():
    mysqld = Mysqld(config_file='tests/data/config_port.cfg')
    assert mysqld.config.database.port == '9999'
