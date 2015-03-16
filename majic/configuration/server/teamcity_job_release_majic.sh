#!/usr/bin/env bash

DB_PASSWORD=$1
CROWD_PASSWORD=$2

MAJIC_SOURCE_PATH="/var/local/majic/jules-jasmin"
VENV="/var/local/majic/virtual_env"

if [ -d "$MAJIC_SOURCE_PATH" ]
then
    sudo -u apache rm -rf "$MAJIC_SOURCE_PATH"
fi

sudo -u apache mkdir "$MAJIC_SOURCE_PATH" || echo "Can not make majic path" || exit 1
sudo -u apache cp -r . "$MAJIC_SOURCE_PATH" || echo "Can not copy majic" || exit 2
cd "$MAJIC_SOURCE_PATH"



cd majic
sudo -u apache sed -i "s#sqlalchemy.url.*#sqlalchemy.url = mysql+mysqlconnector://joj_admin:${DB_PASSWORD}@localhost/joj#g" production.ini
sudo -u apache sed -i "s/password_template/${CROWD_PASSWORD}/g" production.ini

sudo -u apache source $VENV/bin/activate; $VENV/bin/python setup.py install

