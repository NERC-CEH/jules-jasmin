#!/bin/bash

BTICK='`'
EXPECTED_ARGS=3
E_BADARGS=65
MYSQL=`which mysql`

Q1="CREATE DATABASE IF NOT EXISTS ${BTICK}$1${BTICK};"
Q2="GRANT ALL ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost' IDENTIFIED BY '$3';"
Q3="FLUSH PRIVILEGES;"

TEST_DB="${1}_test"

Q4="CREATE DATABASE IF NOT EXISTS ${BTICK}$TEST_DB${BTICK};"
Q5="GRANT ALL ON ${BTICK}$TEST_DB${BTICK}.* TO '$2'@'localhost' IDENTIFIED BY '$3';"
Q6="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}${Q4}${Q5}${Q6}"


if [ $# -ne $EXPECTED_ARGS ]
then
echo "Usage: $0 dbname dbuser dbpass"
exit $E_BADARGS
fi

$MYSQL -u root -p -e "$SQL"

