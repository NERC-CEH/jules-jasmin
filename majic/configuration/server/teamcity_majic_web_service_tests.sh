#!/usr/bin/env bash

VENV="/var/local/majic_ws_test/venv"

source $VENV/bin/activate

cd majic_web_service
sed -i "s#sqlalchemy.url.*#sqlalchemy.url = mysql+mysqlconnector://majic_ws_test_admin:$1@localhost/majic_ws_test#g" test.ini

$VENV/bin/paster setup-app test.ini
$VENV/bin/python setup.py test


