#!/usr/bin/env bash

# As the user who is given sudo permissions delete directories in a file path

DIR_TO_DEL=$1
ROOT_DIR="/tmp/majic_test"

if [ -z "$1" ]
then
   echo "Directory to delete MUST be specified"
   exit -1
fi

if [[ $DIR_TO_DEL == *..* ]]
then
 echo "Bad directory to use. Can not have relative paths in it"
 exit -1
fi

rm -rf ${ROOT_DIR}/${DIR_TO_DEL}
