import os
import pytest
import getpass

from postgresql_integration_test import PostgreSQL


@pytest.mark.pgsql_test
def test_pgsql_init():
    pgsql = PostgreSQL()
    assert pgsql.base_dir is not None


@pytest.mark.pgsql_test
def test_pgsql_run_postmaster():
    pgsql = PostgreSQL()
    instance = pgsql.run()
    assert instance.username == getpass.getuser()


@pytest.mark.pgsql_test
def test_pgsql_tmpdir_delete_norun():
    pgsql = PostgreSQL()
    base_dir = pgsql.base_dir
    pgsql.stop()
    assert not os.path.exists(base_dir)


@pytest.mark.pgsql_test
def test_pgsql_tmpdir_delete_run():
    pgsql = PostgreSQL()
    pgsql.run()
    base_dir = pgsql.base_dir
    pgsql.stop()
    assert not os.path.exists(base_dir)


# Test to see what happens if we try to run an already running instance
@pytest.mark.pgsql_test
def test_pgsql_run_twice():
    with pytest.raises(RuntimeError):
        pgsql = PostgreSQL()
        pgsql.run()
        pgsql.run()

    assert True


# Test to see what happens when postgres binary doesn't exist
@pytest.mark.pgsql_test
def test_pgsql_no_postgres_binary():
    with pytest.raises(RuntimeError):
        pgsql = PostgreSQL()
        pgsql.config.database.postgres_binary = "postgresfake"
        pgsql.run()

    assert True


# Test to see what happens when initdb binary doesn't exist
@pytest.mark.pgsql_test
def test_pgsql_no_initdb_binary():
    with pytest.raises(RuntimeError):
        pgsql = PostgreSQL()
        pgsql.config.database.initdb_binary = "postgresfake"
        pgsql.run()

    assert True


# Test to see what happens when createdb binary doesn't exist
@pytest.mark.pgsql_test
def test_pgsql_no_createdb_binary():
    with pytest.raises(RuntimeError):
        pgsql = PostgreSQL()
        pgsql.config.database.createdb_binary = "postgresfake"
        pgsql.run()

    assert True


# Test to see what happens when createuser binary doesn't exist
@pytest.mark.pgsql_test
def test_pgsql_no_createuser_binary():
    with pytest.raises(RuntimeError):
        pgsql = PostgreSQL()
        pgsql.config.database.createuser_binary = "postgresfake"
        pgsql.run()

    assert True


# Test to see what happens when initdb doesn't work
@pytest.mark.pgsql_test
def test_pgsql_no_dbinit_fails():
    with pytest.raises(FileNotFoundError):
        pgsql = PostgreSQL()
        pgsql.config.dirs.data_dir = "/post/gres/fake"
        pgsql.run()

    assert True
