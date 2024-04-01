import pytest
from mysqld_integration_test import Mysqld
from mysqld_integration_test.helpers import Utils


@pytest.fixture
def mysqld_connect(autouse=True):
    return Mysqld()


@pytest.fixture
def version_mariadb():
    return "mysqld  Ver 10.5.16-MariaDB for Linux on x86_64 (MariaDB Server)"


@pytest.fixture
def version_mysql():
    return "/usr/sbin/mysqld  Ver 8.0.32-0ubuntu0.20.04.2 for Linux on x86_64 ((Ubuntu))"


@pytest.fixture
def version_mysql2():
    return "/usr/libexec/mysqld  Ver 8.0.30 for Linux on x86_64 (Source distribution)"


@pytest.fixture
def version_wontparse():
    return "/usr/libexec/mysqld Ver fakefake"


@pytest.fixture
def version_wrong():
    return "/usr/libexec/mysqld  Ver 3.0.0 for Linux on x86_64 (Source distribution)"


@pytest.mark.helpers_test
def test_find_program_noexists():
    mysqld_location = Utils.find_program("mysqldfake")
    assert mysqld_location is None


@pytest.mark.helpers_test
def test_find_program():
    mysqld_location = Utils.find_program("mysqld")
    assert mysqld_location is not None


@pytest.mark.helpers_test
def test_unused_port_isnum():
    port = Utils.get_unused_port()
    assert isinstance(port, int)


@pytest.mark.helpers_test
def test_unused_port_isinrange():
    port = Utils.get_unused_port()
    assert ((port > 1024) and (port < 65535))


# Test for MariaDB variant
@pytest.mark.helpers_test
def test_parse_version_mariadb_variant(version_mariadb):
    (variant, version_major, version_minor) = Utils.parse_version(version_mariadb)
    assert variant == "mariadb"


# Test for MariaD Bversion major number, also verifies it is an integer
@pytest.mark.helpers_test
def test_parse_version_mariadb_major(version_mariadb):
    (variant, version_major, version_minor) = Utils.parse_version(version_mariadb)
    assert version_major == 10


# Test for MariaDB minor version
@pytest.mark.helpers_test
def test_parse_version_mariadb_minor(version_mariadb):
    (variant, version_major, version_minor) = Utils.parse_version(version_mariadb)
    assert version_minor == '5.16'


# Test for MySQL variant
@pytest.mark.helpers_test
def test_parse_version_mysql_variant(version_mysql):
    (variant, version_major, version_minor) = Utils.parse_version(version_mysql)
    assert variant == "mysql"


# Test for MySQL version major number, also verifies it is an integer
@pytest.mark.helpers_test
def test_parse_version_mysql_major(version_mysql):
    (variant, version_major, version_minor) = Utils.parse_version(version_mysql)
    assert version_major == 8


# Test for MySQL minor version
@pytest.mark.helpers_test
def test_parse_version_mysql_minor(version_mysql):
    (variant, version_major, version_minor) = Utils.parse_version(version_mysql)
    assert version_minor == '0.32'


# Test for MySQL variant
@pytest.mark.helpers_test
def test_parse_version_mysql2_variant(version_mysql2):
    (variant, version_major, version_minor) = Utils.parse_version(version_mysql2)
    assert variant == "mysql"


# Test for MySQL version major number, also verifies it is an integer
@pytest.mark.helpers_test
def test_parse_version_mysql2_major(version_mysql2):
    (variant, version_major, version_minor) = Utils.parse_version(version_mysql2)
    assert version_major == 8


# Test for MySQL minor version
@pytest.mark.helpers_test
def test_parse_version_mysql2_minor(version_mysql2):
    (variant, version_major, version_minor) = Utils.parse_version(version_mysql2)
    assert version_minor == '0.30'


# Test that will fail the parse
@pytest.mark.helpers_test
def test_parse_version_unknown_version(version_wontparse):
    (variant, version_major, version_minor) = Utils.parse_version(version_wontparse)
    assert version_minor is None


# Test that will succeed the parse but will produce bad variant
@pytest.mark.helpers_test
def test_parse_version_unknown_variant(version_wrong):
    (variant, version_major, version_minor) = Utils.parse_version(version_wrong)
    assert variant == 'unknown'
