#!/usr/bin/env bash

VENV="/var/local/majic_test/venv"

source $VENV/bin/activate

cd majic
sed -i "s#sqlalchemy.url.*#sqlalchemy.url = mysql+mysqlconnector://joj_test_admin:$1@localhost/joj_test#g" test.ini
sed -i "s/password_template/$2/g" test.ini

$VENV/bin/python setup.py test
$VENV/bin/paster setup-app test.ini

