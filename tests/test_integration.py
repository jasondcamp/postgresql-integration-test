import pytest
from mysqld_integration_test import Mysqld
import mysql.connector


@pytest.fixture
def mysqld_connect(autouse=True):
    mysqld = Mysqld()
    return mysqld.run()


def execute_query(mysqld, query):
    cnx = mysql.connector.connect(user=mysqld.username,
                                  password=mysqld.password,
                                  host=mysqld.host,
                                  port=mysqld.port, database='test')
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    cursor.close()
    cnx.close()


def select_query(mysqld, query):
    cnx = mysql.connector.connect(user=mysqld.username,
                                  password=mysqld.password,
                                  host=mysqld.host,
                                  port=mysqld.port, database='test')
    cursor = cnx.cursor()
    cursor.execute(query)
    for _result in cursor:
        result = _result
    cursor.close()
    cnx.close()

    return result[0]


# This test makes sure things come up end to end
@pytest.mark.integration_test
def test_mysqld_endtoend(mysqld_connect):
    assert mysqld_connect.username == 'root'


@pytest.mark.integration_test
def test_mysqld_create_table(mysqld_connect):
    execute_query(mysqld_connect,
                  'CREATE TABLE pytest_test (id int4 not null auto_increment, sometext text, primary key(id))')
    assert True


@pytest.mark.integration_test
def test_mysql_insert_into_table(mysqld_connect):
    execute_query(mysqld_connect,
                  'CREATE TABLE pytest_test (id int4 not null auto_increment, sometext text, primary key(id))')
    execute_query(mysqld_connect,
                  "INSERT INTO pytest_test (sometext) VALUES ('this is some text')")
    assert True


@pytest.mark.integration_test
def test_mysql_select_from_table(mysqld_connect):
    execute_query(mysqld_connect,
                  'CREATE TABLE pytest_test (id int4 not null auto_increment, sometext text, primary key(id))')
    execute_query(mysqld_connect,
                  "INSERT INTO pytest_test (sometext) VALUES ('this is some text')")
    select_id = select_query(mysqld_connect, "SELECT id FROM pytest_test")

    assert select_id == 1
