#!/bin/bash
# this script is used to boot a Docker container
#source venv/bin/activate

alembic upgrade head
exec gunicorn -b 0.0.0.0:5000 --log-syslog --timeout 120 run:app
# -w 4 --access-logfile - --error-logfile -