#!/usr/bin/env bash

VENV="/var/local/job_runner_test/venv"

source $VENV/bin/activate

cd job_runner

$VENV/bin/paster setup-app test.ini
$VENV/bin/python setup.py test


