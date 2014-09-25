#!/bin/bash

PRODUCTION_FILE=/var/local/majic/jules-jasmin/majic/production.ini
BACKUP_DIR=/var/local/majic/backups

USERNAME='joj_admin'
PASSWORD=`grep sqlalchemy.url $PRODUCTION_FILE | sed 's/.*://g' | sed 's/@localhost.*//g'`
DATE=`date +%Y_%m_%d_%H_%M`

dump_filename="$BACKUP_DIR/joj_database_$DATE.bck"

mysqldump --databases joj --single-transaction -u joj_admin -p"$PASSWORD" --result-file $dump_filename
EXITCODE=$?

if [ $EXITCODE -ne 0 ] ; then
  echo "Database backup Failed. Check the reason why, see file $dump_filename" | mail -s "FAILED: Database backup" majic@ceh.ac.uk
else
  echo "Database backup Success. Dump is at $dump_filename" | mail -s "success: database backup" majic@ceh.ac.uk
fi

#remove unwanted files
find "$BACKUP_DIR/joj_database_*.bck" -mtime +10 -exec rm {} \;
