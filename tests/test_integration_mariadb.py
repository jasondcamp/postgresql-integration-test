from mysqld_integration_test import Mysqld
import pytest


@pytest.mark.slow
@pytest.mark.integration_test
def test_mysqld_run_mariadb():
    mysqld = Mysqld(mysqld_binary='data/mariadb-10.11.2-linux-systemd-x86_64/bin/mysqld',
                    mysql_install_db_binary='data/mariadb-10.11.2-linux-systemd-x86_64/scripts/mysql_install_db')
    instance = mysqld.run()
    assert instance.username == 'root'
