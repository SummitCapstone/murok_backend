FROM --platform=linux/amd64 python:3.11.6-alpine3.18 as base
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

# Since Dockerfile starts with a Python 3 parent image, set a workdir explicitly.
WORKDIR /usr/src/app
COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

# Install dependencies for mysqlclient
RUN apk update && apk upgrade
RUN apk add --no-cache bash mariadb-dev mariadb-client python3-dev build-base mariadb-common --virtual deps

# Install mysqlclient for Django and MariaDB
RUN pip3 install mysqlclient --no-cache-dir

RUN apk del deps

COPY . .

FROM --platform=linux/amd64 python:3.11.6-alpine3.18 as runner
COPY --from=base /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/
WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /usr/src/app:$PYTHONPATH
EXPOSE 8000

COPY . /usr/src/app/

RUN /bin/sh -c "chmod +x ./entrypoint.sh"

LABEL authors="capella87"

CMD ["python", "-m", "pip", "list"]
