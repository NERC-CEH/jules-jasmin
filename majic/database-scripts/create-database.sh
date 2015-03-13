#!/bin/bash

BTICK='`'
E_BADARGS=65
MYSQL=`which mysql`

Q1="CREATE DATABASE IF NOT EXISTS ${BTICK}$1${BTICK};"
Q2="GRANT ALL ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost' IDENTIFIED BY '$3';"
Q3="FLUSH PRIVILEGES;"

if [ -n "$4" ]
then
    TEST_DB="${1}_test"

    Q4="CREATE DATABASE IF NOT EXISTS ${BTICK}$TEST_DB${BTICK};"
    Q5="GRANT ALL ON ${BTICK}$TEST_DB${BTICK}.* TO '$2'@'localhost' IDENTIFIED BY '$3';"
    Q6="FLUSH PRIVILEGES;"
    SQL="${Q1}${Q2}${Q3}${Q4}${Q5}${Q6}"
fi

if [ $# -ne 3 -a $# -ne 4 ]
then
echo "Usage: $0 dbname dbuser dbpass [test]"
echo "     : test if present will create a test database"
exit $E_BADARGS
fi

$MYSQL -u root -p -e "$SQL"

