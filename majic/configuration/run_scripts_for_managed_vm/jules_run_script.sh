#!/bin/bash
#BSUB –o %J.o
#BSUB –e %J.e
#BSUB –q lotus
#BSUB -n procs_template
#BSUB -m lotusr620

JULES=/group_workspaces/jasmin2/jules_bd/jules_build/jules-vn3.4.1/build/bin/jules.exe

echo "About to run procs_template procs" >out.log
echo "Start Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log

mpirun.lotus $JULES 2>> err.log >> out.log

echo "Post process begin Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log

# create hosts list
rm hosts.txt
export myhosts=($LSB_HOSTS)
for hostName in ${myhosts[*]};do echo $hostName >> hosts.txt ; done

blaunch -u hosts.txt `pwd`/post_process.sh >> out.log 2>> err.log

mv processed/* output
rmdir processed

echo "End Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log
echo "Storage MB: `du -ms`" >> out.log
