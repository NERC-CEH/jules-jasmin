#!/usr/bin/env bash

CONFIGURATION=$1

JOB_RUNNER_SOURCE_PATH="/var/local/job_runner/jules-jasmin"
VENV="/var/local/job_runner/virtual_env"

if [ `whoami` != apache ]
then
  echo "Must be run as apache"
  exit 3
fi

if [ -d "$JOB_RUNNER_SOURCE_PATH" ]
then
    rm -rf "$JOB_RUNNER_SOURCE_PATH"
fi

mkdir "$JOB_RUNNER_SOURCE_PATH" || ( echo "Can not make majic path" && exit 1 )
cp -r . "$JOB_RUNNER_SOURCE_PATH" || ( echo "Can not copy majic" && exit 2 )
cd "$JOB_RUNNER_SOURCE_PATH"



cd job_runner

SECRET=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c20`
sed -i "s/beaker.session.secret/${SECRET}/g" $CONFIGURATION

source $VENV/bin/activate
$VENV/bin/python setup.py install
