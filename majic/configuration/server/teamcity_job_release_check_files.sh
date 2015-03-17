#!/usr/bin/env bash

diff -w /etc/httpd/conf.d/z_majic_runner.conf majic/configuration/apache/z_majic_runner.conf
if [ $? -ne 0 ]
then
   exit 1
fi

diff -w /etc/cron.d/job_status_updater majic/configuration/server/job_status_updater
if [ $? -ne 0 ]
then
   exit 1
fi

diff -w /etc/cron.d/sql_db_backup majic/configuration/server/sql_db_backup
if [ $? -ne 0 ]
then
   exit 1
fi


chkconfig httpd
if [ $? -eq 1 ]
then
   echo "Httpd is not configured to autostart please set this up"
   exit 1
fi

chkconfig crond
if [ $? -eq 1 ]
then
   echo "Crond is not configured to autostart please set this up"
   exit 1
fi
