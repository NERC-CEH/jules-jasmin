#!/bin/bash

LSB_DJOB_NUMPROC=1
LSF_PM_TASKID=1

files=`ls -S output/*.nc | grep -v dump`
i=0
TOTAL=$LSB_DJOB_NUMPROC
#directory below jules-jasmin
source ../../../../../virtual_env/bin/activate
for file in $files
do
   if [ "`expr $i % $TOTAL + 1`" == "$LSF_PM_TASKID" ]
   then
     echo "Converting $i) $file"
     python ../../../../job_runner/job_runner/post_processing_scripts/Convert1Dto2D.py $file >> out_$i.log 2>&1
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
    python ../../../../job_runner/job_runner/post_processing_scripts/convert_fractional_file_for_visualisation.py >> out_land_cover.log 2>&1
    if [ ! $? = 0 ]
    then
       echo "[POST PROCESS ERROR] Post processing of land cover file failed"
    fi
fi
