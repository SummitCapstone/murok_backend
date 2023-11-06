FROM --platform=linux/amd64 python:3.11.6-alpine3.18
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

# Since Dockerfile starts with a Python 3 parent image, set a workdir explicitly.
WORKDIR /app
COPY requirements.txt /app/

RUN pip3 install -r requirements.txt --no-cache-dir

# Install dependencies for mysqlclient
RUN apk update && apk upgrade
RUN apk add --no-cache bash mariadb-dev mariadb-client mariadb-common python3-dev build-base
RUN apk add --no-cache mariadb-connector-c-dev mariadb-embedded mariadb-embedded-dev

RUN pip install --no-cache-dir -r requirements.txt

# Install mysqlclient for Django and MariaDB
RUN pip3 install mysqlclient

RUN apk del build-base

COPY . /app/

EXPOSE 8000

LABEL authors="capella87"

ENTRYPOINT ["top", "-b"]
