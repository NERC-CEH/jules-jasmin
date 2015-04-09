#!/usr/bin/env bash

DB_PASSWORD=$1
CONFIGURATION=$2

MAJIC_SOURCE_PATH="/var/local/majic/jules-jasmin"
VENV="/var/local/majic/virtual_env"

cd majic
sed -i "s#sqlalchemy.url.*#sqlalchemy.url = mysql+mysqlconnector://joj_admin:${DB_PASSWORD}@localhost/joj#g" $CONFIGURATION
sed -i "s/password_template/${CROWD_PASSWORD}/g" $CONFIGURATION

sudo -u mysql /var/local/majic/jules-jasmin/majic/joj/cron_scripts/database_backup_and_maintenance.sh

source $VENV/bin/activate
alembic -c $CONFIGURATION upgrade head
