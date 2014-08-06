#!/bin/bash

echo "About to run procs_template procs" >>out.log
echo "Start Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log
./jules_3_4_1.exe 2>> err.log >> out.log

echo "Post processing start: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log
source ./virtualenv/bin/activate
python Convert1Dto2D.py

mv output x_output
mv processed output

echo "End Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log
echo "Storage MB: `du -ms`" >> out.log

