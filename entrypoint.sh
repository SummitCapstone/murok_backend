#!/bin/sh

python manage.py migrate;
python manage.py makemigrations;
python manage.py migrate;
python manage.py createsuperuser --noinput || true;

hypercorn murok_backend.asgi:application --bind 0.0.0.0:8888 --reload
