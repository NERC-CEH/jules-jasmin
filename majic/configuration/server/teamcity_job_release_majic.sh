#!/usr/bin/env bash

DB_PASSWORD=$1
CROWD_PASSWORD=$2
CONFIGURATION=$3

MAJIC_SOURCE_PATH="/var/local/majic/jules-jasmin"
VENV="/var/local/majic/virtual_env"

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

cd majic
sed -i "s#sqlalchemy.url.*#sqlalchemy.url = mysql+mysqlconnector://joj_admin:${DB_PASSWORD}@localhost/joj#g" $CONFIGURATION
sed -i "s/password_template/${CROWD_PASSWORD}/g" $CONFIGURATION
sed -i "s/beaker.session.secret/${SECRET}/g" $CONFIGURATION

source $VENV/bin/activate
$VENV/bin/python setup.py install

