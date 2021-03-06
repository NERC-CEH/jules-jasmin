#!/bin/bash

CONFIGURATION_FILE=/var/local/majic/jules-jasmin/majic/production.ini
BACKUP_DIR=/var/local/majic_backups
USERNAME='joj_admin'

if [ -n "$1" ]
then
    CONFIGURATION_FILE=$1
fi

PASSWORD=`grep sqlalchemy.url $CONFIGURATION_FILE | sed 's/.*://g' | sed 's/@localhost.*//g'`
DATE=`date +%Y_%m_%d_%H_%M`

dump_filename="$BACKUP_DIR/joj_database_$DATE.bck"

mysqldump --databases joj --single-transaction -u $USERNAME -p"$PASSWORD" --result-file $dump_filename
EXITCODE=$?

chgrp sqlbackup $dump_filename
chmod 640 $dump_filename

if [ $EXITCODE -ne 0 ] ; then
  echo "$DATE: Database backup Failed."
  echo "$DATE: Database backup Failed. Check the reason why, see file $dump_filename" | mail -s "FAILED: Database backup" majic@ceh.ac.uk
  echo "$DATE: Database backup Failed. Check the reason why, see file $dump_filename" | mail -s "FAILED: Database backup" majic.support@tessella.com
  echo "$DATE: Database backup Failed. Check the reason why, see file $dump_filename" | mail -s "FAILED: Database backup" kerg@tessella.com
  echo "$DATE: Database backup Failed. Check the reason why, see file $dump_filename" | mail -s "FAILED: Database backup" misc@tessella.com
  exit -1
else
  echo "$DATE: Database backup Success."
  echo "$DATE: Database backup Success. Dump is at $dump_filename" | mail -s "success: database backup" majic@ceh.ac.uk
  echo "$DATE: Database backup Success. Dump is at $dump_filename" | mail -s "success: database backup" kerg@tessella.com
  echo "$DATE: Database backup Success. Dump is at $dump_filename" | mail -s "success: database backup" misc@tessella.com
fi

#remove unwanted files
find $BACKUP_DIR -name "joj_database_*.bck" -mtime +10 -exec rm {} \;

exit 0