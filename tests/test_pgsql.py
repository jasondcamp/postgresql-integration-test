from postgresql_integration_test import postgresql
import os
import pytest


@pytest.mark.pgsql_test
def test_pgsql_init():
    pgsql = postgresql.PostgreSQL()
    assert pgsql.base_dir is not None


@pytest.mark.pgsql_test
def test_pgsql_run_postmaster():
    pgsql = postgresql.PostgreSQL()
    instance = pgsql.run()
    assert instance.username == "imeyer"


@pytest.mark.pgsql_test
def test_pgsql_tmpdir_delete():
    pgsql = postgresql.PostgreSQL()
    base_dir = pgsql.base_dir
    s = pgsql.run()
    assert not os.path.exists(base_dir)
