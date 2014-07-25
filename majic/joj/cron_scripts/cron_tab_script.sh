#!/bin/bash

source /home/matken/projectenv/bin/activate

cd /home/matken/jules-jasmin/majic/joj/cron_scripts

python /home/matken/jules-jasmin/majic/joj/cron_scripts/update_job_statuses.py development.ini 2>> /home/matken/jules-jasmin/majic/joj/cron_scripts/out.log >> /home/matken/jules-jasmin/majic/joj/cron_scripts/out.log

