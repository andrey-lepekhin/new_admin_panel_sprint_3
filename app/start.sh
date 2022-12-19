#!/usr/bin/env bash

app/wait-for-it.sh pg_db:5432 --timeout=10 --strict -- \
  python app/manage.py makemessages --locale=ru --locale=en &&\
  python app/manage.py compilemessages --locale=ru --locale=en &&\
  python app/manage.py collectstatic --noinput &&\
  uwsgi --chdir=app --ini app/uwsgi.ini
