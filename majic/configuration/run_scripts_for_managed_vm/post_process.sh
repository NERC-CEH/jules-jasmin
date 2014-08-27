#!/bin/bash

JOB_RUNNER_DIR=/var/local/job_runner
CONVERT_SCRIPT=$JOB_RUNNER_DIR/jules-jasmin/job_runner/job_runner/post_processing_scripts/Convert1Dto2D.py

files=`ls -S output/*.nc | grep -v dump`
i=0
TOTAL=$LSB_DJOB_NUMPROC
source $JOB_RUNNER_DIR/virtual_env/bin/activate
for file in $files
do
   echo "Converting $file"
   if [ "`expr $i % $TOTAL + 1`" == "$LSF_PM_TASKID" ]
   then
     python $CONVERT_SCRIPT $file 2>> err_$LSF_PM_TASKID.log >> out_$LSF_PM_TASKID.log
     if [ $? = 0 ]
     then
        rm $file
     else
       echo "[POST PROCESS ERROR] Post processing of $file failed"
     fi
   fi
   i=`expr $i + 1`
done

