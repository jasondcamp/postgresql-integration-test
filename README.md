# postgresql-integration-test
![](https://img.shields.io/pypi/v/postgresql-integration-test.svg) ![](https://img.shields.io/badge/status-alpha-red) ![](https://github.com/jasondcamp/postgresql-integration-test/actions/workflows/postgresql-integration-test.yml/badge.svg)  ![](https://img.shields.io/pypi/pyversions/postgresql-integration-test.svg) ![](https://img.shields.io/badge/license-Apache-lightgrey)

![](https://api.codeclimate.com/v1/badges/c4e922d83662be40871c/maintainability) ![](https://api.codeclimate.com/v1/badges/c4e922d83662be40871c/test_coverage)

## Overview
postgresql-integration-test is a python module that creates a temporary PostgreSQL instance to use for testing your application. You will need a working PostgreSQL install. It does not have to be running, the binaries are needed.

## Download and Install
To install use pip:

    $ pip install postgresql-integration-test

Or clone the repo:

    $ git clone https://github.com/jasondcamp/postgresql-integration-test.git

## Configuration
### Class arguments
The following class arguments can be overridden by passing them in, these arguments will override the config file arguments.
| Argument | Description | Default |
| --------------- | -------------- | -------------- |
|username|Username for database|root|
|password|Password for database|root|
|host|Host to bind|127.0.0.1|
|port|Port to bind|random|
|postgres_binary|Location of postgres binary|Searches paths|
|timeout_start|Timeout to start PostgreSQL|30 seconds|
|timeout_stop|Timeout to stop PostgreSQL|30 seconds|
|log_level|Log level|INFO|
|config_file|Configuration file|postgresql-integration-test.cfg|

### postgresql-integration-test config file
Default settings can be overridden in  a config file. The default name is `posgresql-integration-test.cfg` in the local directory and can be overridden by passing in the `config` option to the instance creation.

#### Example config
```
database:
  host: '127.0.0.1'
  port: '9999'
  username: 'root'
  password: 'test'
  postgresql_binary: '/usr/sbin/mysqld'

general:
  log_level: 'DEBUG'
  timeout_start: 30
  timeout_stop: 30
```


## Usage

#### import

```
from postgresql_integration_test import PostgreSQL
```

#### run
Starts up the postgresql server

```
postgresql = PostgreSQL()
instance = postgresql.run()
```

#### stop
Stops the postgres server
```
postgresql.stop()
```

### Example Code

```
#!/usr/bin/env python3

from postgresql_integration_test import PostgreSQL
import psycopg2

postgresql = PostgreSQL(config='/some/dir/postgresql-integration-test.cfg')
instance = postgres.run()

# Make query to database
cnx = mysql.connector.connect(user=instance.username, password=instance.password,
                      host=instance.host, port=instance.port)
cursor = cnx.cursor()
cursor.execute(f"SHOW databases;")

for db in cursor:
   print(db[0])

cursor.close()
cnx.close()

mysqld.stop()
```



