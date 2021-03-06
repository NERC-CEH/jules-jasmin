#!/usr/bin/env bash

DB_PASSWORD=$1
CONFIGURATION=$2

MAJIC_SOURCE_PATH="/var/local/majic_ws/jules-jasmin"
VENV="/var/local/majic_ws/virtual_env"

if [ `whoami` != apache ]
then
  echo "Must be run as apache"
  exit 3
fi

if [ -d "$MAJIC_SOURCE_PATH" ]
then
    rm -rf "$MAJIC_SOURCE_PATH"
fi

mkdir "$MAJIC_SOURCE_PATH" || ( echo "Can not make majic path" && exit 1 )
cp -r . "$MAJIC_SOURCE_PATH" || ( echo "Can not copy majic" && exit 2 )
cd "$MAJIC_SOURCE_PATH"

SECRET=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c20`

cd majic_web_service
sed -i "s#sqlalchemy.url.*#sqlalchemy.url = mysql+mysqlconnector://joj_reader:${DB_PASSWORD}@localhost/joj#g" $CONFIGURATION
sed -i "s/beaker.session.secret.*/beaker.session.secret = ${SECRET}/g" $CONFIGURATION

source $VENV/bin/activate
$VENV/bin/python setup.py install

