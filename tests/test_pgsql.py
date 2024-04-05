import os
import pytest
import getpass

from postgresql_integration_test import postgresql


@pytest.mark.pgsql_test
def test_pgsql_init():
    pgsql = postgresql.PostgreSQL()
    assert pgsql.base_dir is not None


@pytest.mark.pgsql_test
def test_pgsql_run_postmaster():
    pgsql = postgresql.PostgreSQL()
    instance = pgsql.run()
    assert instance.username == getpass.getuser()


@pytest.mark.pgsql_test
def test_pgsql_tmpdir_delete():
    pgsql = postgresql.PostgreSQL()
    base_dir = pgsql.base_dir
    pgsql.close()
    assert not os.path.exists(base_dir)
