#!/usr/bin/env bash

# As the user who is given sudo permissions delete directories in a file path

DIR_TO_SET_PERMISSIONS_ON="$1"
OWNER="$2"
IS_PUBLISHED="$3"
IS_PUBLIC="$4"
ROOT_DIR="/data/public/majic"


if [ -z "$DIR_TO_SET_PERMISSIONS_ON" -o  -z "$OWNER" -o -z "$IS_PUBLISHED" -o -z "$IS_PUBLIC" ]
then
   echo "All arguments must be non-zero"
   exit -1
fi

if [[ $DIR_TO_SET_PERMISSIONS_ON == *..* ]]
then
 echo "Bad directory to use. Can not have relative paths in it"
 exit -1
fi

if [ "$IS_PUBLISHED" == "set_for_writing" ]
then
  chown -R ${OWNER}:majic ${ROOT_DIR}/${DIR_TO_SET_PERMISSIONS_ON} || exit -2
  chmod -R go-r,u+w ${ROOT_DIR}/${DIR_TO_SET_PERMISSIONS_ON} || exit -1
  exit 0
fi

chown -R ${OWNER}:majic ${ROOT_DIR}/${DIR_TO_SET_PERMISSIONS_ON} || exit -2
if [ "$IS_PUBLISHED" == "True" -a "$IS_PUBLIC" = "True" ]
then
 chmod -R go+rx,a-w ${ROOT_DIR}/${DIR_TO_SET_PERMISSIONS_ON} || exit -1
elif [ "$IS_PUBLISHED" == "False" -a "$IS_PUBLIC" = "True" ]
then
 chmod -R g-rx,o+rx,a-w ${ROOT_DIR}/${DIR_TO_SET_PERMISSIONS_ON} || exit -1
elif [ "$IS_PUBLISHED" == "True" -a "$IS_PUBLIC" = "False" ]
then
 chmod -R g+rx,o-rx,a-w ${ROOT_DIR}/${DIR_TO_SET_PERMISSIONS_ON} || exit -1
elif [ "$IS_PUBLISHED" == "False" -a "$IS_PUBLIC" = "False" ]
then
 chmod -R go-rx,a-w ${ROOT_DIR}/${DIR_TO_SET_PERMISSIONS_ON} || exit -1
fi

find ${ROOT_DIR}/${DIR_TO_SET_PERMISSIONS_ON} -type d -exec chmod g+rx {} \;
