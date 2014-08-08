#!/bin/bash

files=`ls -S output/*.nc | grep -v dump`
i=0
TOTAL=$LSB_DJOB_NUMPROC
source ./virtualenv/bin/activate
for file in $files
do
   echo "Converting $file"
   if [ "`expr $i % $TOTAL + 1`" == "$LSF_PM_TASKID" ]
   then
     python Convert1Dto2D.py $file >> out_$LSF_PM_TASKID.log
     if [ $? = 0 ]
     then
        rm $file
     else
       echo "[POST PROCESS ERROR] Post processing of $file failed"
     fi
   fi
   i=`expr $i + 1`
done

