import pytest
from postgresql_integration_test.helpers import Utils


@pytest.fixture
def version_postgres():
    return "postgres (PostgreSQL) 10.23"


@pytest.fixture
def version_postgres2():
    return "postgres (PostgreSQL) 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1)"


@pytest.fixture
def version_wontparse():
    return "postGRESQL (PostgreSQL) seven"


@pytest.fixture
def version_wrong():
    return "postfake (PostgreSQL) 7.5"


@pytest.mark.helpers_test
def test_unused_port_isnum():
    port = Utils.get_unused_port()
    assert isinstance(port, int)


@pytest.mark.helpers_test
def test_unused_port_isinrange():
    port = Utils.get_unused_port()
    assert (port > 1024) and (port < 65535)


# Test for PostgreSQL version major number, also verifies it is an integer
@pytest.mark.helpers_test
def test_parse_version_postgres_major(version_postgres):
    (variant, version_major, version_minor) = Utils.parse_version(version_postgres)
    assert version_major == 10


# Test for PostgreSQL minor version
@pytest.mark.helpers_test
def test_parse_version_postgres_minor(version_postgres):
    (variant, version_major, version_minor) = Utils.parse_version(version_postgres)
    assert version_minor == 23


# Test for PostgreSQL variant
@pytest.mark.helpers_test
def test_parse_version_postgres_variant(version_postgres):
    (variant, version_major, version_minor) = Utils.parse_version(version_postgres)
    assert variant == "postgres"


# Test that will fail the parse
@pytest.mark.helpers_test
def test_parse_version_unknown_version(version_wontparse):
    (variant, version_major, version_minor) = Utils.parse_version(version_wontparse)
    assert version_minor is None


# Test that will succeed the parse but will produce bad variant
@pytest.mark.helpers_test
def test_parse_version_unknown_variant(version_wrong):
    (variant, version_major, version_minor) = Utils.parse_version(version_wrong)
    assert variant == "postfake"
