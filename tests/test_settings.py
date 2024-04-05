import pytest
import functools

from postgresql_integration_test.postgresql import PostgreSQL


@pytest.fixture
def pgsql_connect(autouse=True):
    return PostgreSQL()


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


# Make sure config options exists and check some defaults
@pytest.mark.settings_test
def test_settings_test(pgsql_connect):
    assert rgetattr(pgsql_connect, "config") is not None


@pytest.mark.settings_test
def test_dirs_basedir_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.dirs.base_dir") is not None


@pytest.mark.settings_test
def test_dirs_datadir_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.dirs.data_dir") is not None


@pytest.mark.settings_test
def test_dirs_etcdir_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.dirs.etc_dir") is not None


@pytest.mark.settings_test
def test_dirs_tmpdir_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.dirs.tmp_dir") is not None


@pytest.mark.settings_test
def test_database_host_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.database.host") is not None


@pytest.mark.settings_test
def test_database_port_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.database.port") is not None


@pytest.mark.settings_test
def test_datbase_username_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.database.username") is not None


@pytest.mark.settings_test
def test_pg_ctl_binary_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.database.postgres_binary") is not None


@pytest.mark.settings_test
def test_general_timeoutstart_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.general.timeout_start") is not None


@pytest.mark.settings_test
def test_general_timeoutstop_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.general.timeout_stop") is not None


@pytest.mark.settings_test
def test_general_loglevel_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.general.log_level") is not None


@pytest.mark.settings_test
def test_general_configfile_exists(pgsql_connect):
    assert rgetattr(pgsql_connect, "config.general.config_file") is not None


# Test that a config option that we know doesn't exist does not exist
@pytest.mark.settings_test
def test_general_faketest_notexists(pgsql_connect):
    with pytest.raises(AttributeError):
        _ = rgetattr(pgsql_connect, "config.general.faketest") is None


# Test a config option passed in as an argument works
@pytest.mark.settings_test
def test_arg_config_option_exists():
    pgsql = PostgreSQL(port="8888")
    assert pgsql.config.database.port == "8888"


# Test that a config file option works
@pytest.mark.settings_test
def test_config_file_option_exists():
    pgsql = PostgreSQL(config_file="tests/data/config_port.cfg")
    assert pgsql.config.database.port == "9999"
