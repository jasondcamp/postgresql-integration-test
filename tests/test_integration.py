import pytest
import psycopg2
import getpass

from postgresql_integration_test.postgresql import PostgreSQL


@pytest.fixture
def pgsql_connect():
    pgsql = PostgreSQL()
    return pgsql.run()


def execute_query(pgsql, query):
    cnx = psycopg2.connect(
        user=pgsql.username,
        host=pgsql.host,
        port=pgsql.port,
        database="test",
    )
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    cursor.close()
    cnx.close()


def select_query(pgsql, query):
    cnx = psycopg2.connect(
        user=pgsql.username,
        host=pgsql.host,
        port=pgsql.port,
        database="test",
    )
    cursor = cnx.cursor()
    cursor.execute(query)
    for _result in cursor:
        result = _result
    cursor.close()
    cnx.close()

    return result[0]


# This test makes sure things come up end to end
@pytest.mark.integration_test
def test_pgsql_endtoend(pgsql_connect):
    assert pgsql_connect.username == getpass.getuser()


@pytest.mark.integration_test
def test_pgsql_create_table(pgsql_connect):
    execute_query(
        pgsql_connect,
        "CREATE TABLE test (id serial primary key, sometext text)",
    )
    assert True


@pytest.mark.integration_test
def test_pgsql_insert_into_table(pgsql_connect):
    execute_query(
        pgsql_connect,
        "CREATE TABLE test (id serial primary key, sometext text)",
    )
    execute_query(
        pgsql_connect, "INSERT INTO test (sometext) VALUES ('this is some text')"
    )
    assert True


@pytest.mark.integration_test
def test_pgsql_select_from_table(pgsql_connect):
    execute_query(
        pgsql_connect,
        "CREATE TABLE test (id serial primary key, sometext text)",
    )
    execute_query(
        pgsql_connect, "INSERT INTO test (sometext) VALUES ('this is some text')"
    )

    select_id = select_query(pgsql_connect, "SELECT id FROM test")

    assert select_id == 1
