#!/bin/bash
MODEL_RUN_DIR=`pwd`
JOB_RUNNER_DIR=/var/local/job_runner

sed "s/procs_template/8/g" $JOB_RUNNER_DIR/run_scripts/jules_run_script.sh | sed "s:model_run_dir_template:$MODEL_RUN_DIR:g" > jules_run.sh

cp $JOB_RUNNER_DIR/run_scripts/post_process.sh .

chmod g+wr output
chmod g+wr .

sudo -i -u jules-bd-robot /home/users/jules-bd-robot/submit.sh < jules_run.sh
