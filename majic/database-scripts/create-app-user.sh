#!/bin/bash


BTICK='`'
EXPECTED_ARGS=3
E_BADARGS=65
MYSQL=`which mysql`
TEST_DB="${1}_test"

Q1="GRANT SELECT ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost' IDENTIFIED BY '$3';"
Q2="GRANT INSERT ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost';"
Q3="GRANT UPDATE ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost';"
Q4="GRANT DELETE ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost';"
Q5="GRANT EXECUTE ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost';"
Q6="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}${Q4}${Q5}${Q6}"

Q1="GRANT SELECT ON ${BTICK}$TEST_DB${BTICK}.* TO '$2'@'localhost';"
Q2="GRANT INSERT ON ${BTICK}$TEST_DB${BTICK}.* TO '$2'@'localhost';"
Q3="GRANT UPDATE ON ${BTICK}$TEST_DB${BTICK}.* TO '$2'@'localhost';"
Q4="GRANT DELETE ON ${BTICK}$TEST_DB${BTICK}.* TO '$2'@'localhost';"
Q5="GRANT EXECUTE ON ${BTICK}$TEST_DB${BTICK}.* TO '$2'@'localhost';"
Q6="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}${Q4}${Q5}${Q6}"


if [ $# -ne $EXPECTED_ARGS ]
then
echo "Usage: $0 dbname dbuser dbpass"
exit $E_BADARGS
fi

$MYSQL -uroot -p -e "$SQL"

