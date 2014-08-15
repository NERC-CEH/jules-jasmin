#!/bin/bash

JOB_RUNNER_DIR=/group_workspaces/jasmin2/jules_bd/job_runner

sed "s/procs_template/1/g" $JOB_RUNNER_DIR/run_scripts/jules_run_script.sh > jules_run.sh

chmod g+wr output
chmod g+wr .

sudo -i -u jules-bd-robot /home/users/jules-bd-robot/submit.sh < jules_run.sh 
