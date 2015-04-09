#!/usr/bin/env bash

DB_PASSWORD=$1
CROWD_PASSWORD=$2
CONFIGURATION=$3

MAJIC_SOURCE_PATH="/var/local/majic/jules-jasmin"
VENV="/var/local/majic/virtual_env"

cd majic
sed -i "s#sqlalchemy.url.*#sqlalchemy.url = mysql+mysqlconnector://joj_admin:${DB_PASSWORD}@localhost/joj#g" $CONFIGURATION
sed -i "s/password_template/${CROWD_PASSWORD}/g" $CONFIGURATION

alembic -c $CONFIGURATION upgrade head
