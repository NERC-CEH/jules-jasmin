#!/bin/bash

JOB_RUNNER_DIR=/group_workspaces/jasmin2/jules_bd/job_runner/post_processing
CONVERT_SCRIPT=$JOB_RUNNER_DIR/Convert1Dto2D.py
LAND_COVER_CONVERT_SCRIPT=$JOB_RUNNER_DIR/convert_fractional_file_for_visualisation.py

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
   if [ "`expr $i % $TOTAL + 1`" == "$LSF_PM_TASKID" ]
   then
     echo "Converting $file"
     python $CONVERT_SCRIPT $file >> out_$i.log 2>&1
     finished=`grep -c 'Post processing finished' out_$i.log`
     if [ "$finished" -eq 1 ]
     then
        rm $file
     else
       echo "[POST PROCESS ERROR] Post processing of $file failed"
     fi
   fi
   i=`expr $i + 1`
done

if [ "$LSF_PM_TASKID" == 1 ]
then
    python $LAND_COVER_CONVERT_SCRIPT >> out_land_cover.log 2>&1
    if [ ! $? = 0 ]
    then
       echo "[POST PROCESS ERROR] Post processing of land cover file failed"
    fi
fi
