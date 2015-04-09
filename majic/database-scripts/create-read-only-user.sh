#!/bin/bash


BTICK='`'
EXPECTED_ARGS=3
E_BADARGS=65
MYSQL=`which mysql`

Q1="GRANT SELECT ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost' IDENTIFIED BY '$3';"
Q2="GRANT EXECUTE ON ${BTICK}$1${BTICK}.* TO '$2'@'localhost';"
Q3="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}"



if [ $# -ne $EXPECTED_ARGS ]
then
echo "Usage: $0 dbname dbuser dbpass"
exit $E_BADARGS
fi

$MYSQL -uroot -p -e "$SQL"

