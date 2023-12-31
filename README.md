# Murok-Backend 무럭무럭 백엔드
2023-2 Capstone Design Project by Team Summit

## Requirements
### Prerequisites
* Django 4.2.x
* Python 3.11 or later
* Django REST Framework 3.14.0 or later
* MariaDB 10.11.x (LTS) or later (Tested in 11.2.x with problems. See troubleshooting)
* RabbitMQ 3.12.x or later
* Erlang 26.1.x or later
* Caddy Server V2
* Other requirements are in requirements.txt

To configure frontend development environment, see frontend one.

Note: Web server, CI/CD or Docker deployment is under consideration.

Also, we recommend using PyCharm as the IDE for this project. PyCharm related configuration 
files are also committed for convenience. 

Host OS is not matter. We've tested on both Windows 10 and Ubuntu 22.04 LTS.

In recently (Oct 2023), Python 3.12 is released, we've not deployed the version due to 
the lack of our dependencies' corresponding versions.

Because of MariaDB's features, Using equivalent MySQL version is also accepted and should be worked well, but we strongly recommended to use MariaDB for performance and compatibility.

There's another MySQL-compatible database, Dolt, it is not tested yet.

### Installation
1. Clone this repository.
2. Install the prerequisites above and dependencies in requirements.txt. Venv is required.
3. Install mysqlclient package to connect to MariaDB. If you have a trouble in
4. Access MariaDB and make a database named 'murok'.
5. Make a new account for its admin and grant permissions to it.
```mariadb
CREATE DATABASE 'murok';
CREATE USER 'whatever'@'localhost' IDENTIFIED BY 'Whatever you want';
GRANT ALL PRIVILEGES ON murok.* TO 'murok'@'localhost';
```
6. Generate secrets.json file and put secrets. (See below)
7. Make dbconnection.cnf for database connection information. (See below)
8. Set 'read_default_file' to dbconnection.cnf in settings.py.
9. Run the server with the following command.

**WARNING**: To prevent stuck in migration work, Please migrate ```accounts``` app explicitly first.

```shell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

10. Make a superuser account in Django Admin with the following command.
```shell
python manage.py createsuperuser
```
11. Access the server with the following URL.
```url
python manage.py runserver
```

#### secrets.json Format
The secrets.json is a distinct JSON file that contains secret key for Django.
```json
{
  "SECRET_KEY": "Django secret key"
}
```

To get a secret key, Use the following command in the project root directory under virtualenv activation.
```shell
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Other elements are currently included:
* EMAIL_HOST_USER
* EMAIL_HOST_PASSWORD

#### dbconnection.cnf Format
```ini
[client]
database = murok
user = whatever
password = whatever you want
default-character-set = utf8
host = 127.0.0.1
port = 3306
```

## Deployment
### WSGI - Hypercorn
To run the server via WSGI, use the following command.
```shell
hypercorn murok_backend.asgi:application --bind [IP]:[Port] --reload
```
QUIC bind will be appended later.

#### HTTPS Support
To support HTTP/2 and HTTP/3, we must use HTTPS.
**This section is Under Construction.**

### CI/CD
Not yet. We're considering Docker and GitHub Actions.

### Server Deployment

#### Run on Internet Information Services (IIS)

#### Run on NGINX

#### Run on Caddy V2 Server

#### Run on Docker

## Troubleshooting
### Database Configurations
#### MySQLClient Problem with MariaDB 11.x
It is no problem when you installed the latest version of MySQL as of Nov 2023.

In this situation, They require ```libmysqlclient22``` package to install. That package is included in MySQL APT Repository.
Visit the [MySQL Download Page](https://dev.mysql.com/downloads/repo/apt/) and install the package.
After updating APT information, you can install ```libmysqlclient22```

Also, Set a custom build of mysqlclient.
```bash
$ export MYSQLCLIENT_CFLAGS=`pkg-config mysqlclient --cflags`
$ export MYSQLCLIENT_LDFLAGS=`pkg-config mysqlclient --libs`
$ pip install mysqlclient
```

---
Copyright © 2023 Team Summit; Capella87 and LeeDayDay
