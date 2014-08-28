#!/bin/bash

JOB_RUNNER_DIR=/group_workspaces/jasmin2/jules_bd/job_runner/post_processing
CONVERT_SCRIPT=$JOB_RUNNER_DIR/Convert1Dto2D.py

files=`ls -S output/*.nc | grep -v dump`
i=0
TOTAL=1
if [ ! -z "$LSB_DJOB_NUMPROC" ]
then
  TOTAL=$LSB_DJOB_NUMPROC
fi
if [ -z "$LSF_PM_TASKID" ]
then
  LSF_PM_TASKID=0
fi

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

