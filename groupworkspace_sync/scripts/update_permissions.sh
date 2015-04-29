#!/usr/bin/env bash

# As the user who is given sudo permissions delete directories in a file path

DIR_TO_DEL="$1"
OWNER="$2"
IS_PUBLISHED="$3"
IS_PUBLIC="$4"
ROOT_DIR="/data/public/majic"


if [ -z "$DIR_TO_DEL" -o  -z "$OWNER" -o -z "$IS_PUBLISHED" -o -z "$IS_PUBLIC" ]
then
   echo "All arguments must be non-zero"
   exit -1
fi

if [[ $DIR_TO_DEL == *..* ]]
then
 echo "Bad directory to use. Can not have relative paths in it"
 exit -1
fi

chown -R ${OWNER}:majic ${ROOT_DIR}/${DIR_TO_DEL} || exit -2
if [ "$IS_PUBLISHED" == "True" -a "$IS_PUBLIC" = "True" ]
then
 chmod -R go+r,a-w ${ROOT_DIR}/${DIR_TO_DEL} || exit -1
elif [ "$IS_PUBLISHED" == "False" -a "$IS_PUBLIC" = "True" ]
then
 chmod -R g-r,o+r,a-w ${ROOT_DIR}/${DIR_TO_DEL} || exit -1
elif [ "$IS_PUBLISHED" == "True" -a "$IS_PUBLIC" = "False" ]
then
 chmod -R g+r,o-r,a-w ${ROOT_DIR}/${DIR_TO_DEL} || exit -1
elif [ "$IS_PUBLISHED" == "False" -a "$IS_PUBLIC" = "False" ]
then
 chmod -R go-r,a-w ${ROOT_DIR}/${DIR_TO_DEL} || exit -1
fi
