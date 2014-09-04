#!/bin/bash

VENV="/var/local/majic/virtual_env"

source $VENV/bin/activate

cd "/var/local/majic/jules-jasmin/majic"
export REQUESTS_CA_BUNDLE=/var/local/ssl/job_runner.crt

python joj/cron_scripts/update_job_statuses.py production.ini 2>&1 >> /var/local/majic/logs/cron_job.log
