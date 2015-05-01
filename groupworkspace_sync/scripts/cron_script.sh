#!/usr/bin/env bash
# run the job if it is not already running

if [ `ps -u majic_sync | grep -c python` == 0 ]
then
  /var/local/majic_sync/virtualenv/bin/python -m sync.synchroniser /var/local/majic_sync/jules-jasmin/groupworkspace_sync/production.ini
fi

