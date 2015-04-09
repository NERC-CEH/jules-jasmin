#!/usr/bin/env bash

DB_PASSWORD=$1
CONFIGURATION=$2

MAJIC_SOURCE_PATH="/var/local/majic/jules-jasmin"
VENV="/var/local/majic/virtual_env"

cd majic
sed -i "s#sqlalchemy.url.*#sqlalchemy.url = mysql+mysqlconnector://joj_admin:${DB_PASSWORD}@localhost/joj#g" $CONFIGURATION
sed -i "s/password_template/${CROWD_PASSWORD}/g" $CONFIGURATION

dump_filename="$PWD/dump_filename"
mysqldump --databases joj --single-transaction -u joj_admin -p"DB_PASSWORD" --result-file $dump_filename
EXITCODE=$?
if [ $EXITCODE -ne 0 ] ; then
  echo "Database backup Failed."
  echo "Database backup Failed. Check the reason why, see file $dump_filename"
  exit -1
else
  echo "Database backup Success. Dump is at $dump_filename"
fi

echo "Database dump created in $PWD/dump_filename"

source $VENV/bin/activate
alembic -c $CONFIGURATION upgrade head
