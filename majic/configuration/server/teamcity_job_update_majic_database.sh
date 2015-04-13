#!/usr/bin/env bash

DB_PASSWORD=$1
CONFIGURATION=$2

MAJIC_SOURCE_PATH="/var/local/majic/jules-jasmin"
VENV="/var/local/majic/virtual_env"

cd majic

sudo -u mysql /var/local/majic/jules-jasmin/majic/joj/cron_scripts/database_backup_and_maintenance.sh ${DB_PASSWORD} || exit 1

source $VENV/bin/activate
alembic -c $MAJIC_SOURCE_PATH/majic/$CONFIGURATION upgrade head
