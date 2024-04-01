from mysqld_integration_test import Mysqld
import os
import pytest
# import pytest_mock


@pytest.mark.mysqld_test
def test_mysqld_init():
    mysqld = Mysqld()
    assert mysqld.base_dir is not None


@pytest.mark.mysqld_test
def test_mysqld_run_mariadb():
    mysqld = Mysqld()
    instance = mysqld.run()
    assert instance.username == 'root'


@pytest.mark.mysqld_test
def test_mysqld_run_mysql():
    mysqld = Mysqld()
    instance = mysqld.run()
    assert instance.username == 'root'


@pytest.mark.mysqld_test
def test_mysqld_tmpdir_delete():
    mysqld = Mysqld()
    base_dir = mysqld.base_dir
    mysqld.close()
    assert not os.path.exists(base_dir)
