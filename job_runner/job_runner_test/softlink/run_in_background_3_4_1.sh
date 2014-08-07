#!/bin/bash

echo "About to run procs_template procs" >>out.log
echo "Start Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log
./jules_3_4_1.exe 2>> err.log >> out.log

echo "Post processing start: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log

./post_process.sh  >> out.log

mv processed/* output
rmdir processed

echo "End Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log
echo "Storage MB: `du -ms`" >> out.log

