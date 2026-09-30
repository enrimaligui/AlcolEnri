#!/usr/bin/env bash
set -e
python -m pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py crear_inicial
python manage.py collectstatic --noinput
