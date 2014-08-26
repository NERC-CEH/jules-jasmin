#!/bin/bash
#BSUB –o %J.o
#BSUB –e %J.e
#BSUB –q lotus
#BSUB -n procs_template
#BSUB -m lotusr620

cd model_run_dir_template

JOB_RUNNER_DIR=/var/local/job_runner
JULES=/group_workspaces/jasmin2/jules_bd/jules_build/jules-vn3.4.1_dailydisagg/build/bin/jules.exe

echo "About to run procs_template procs in `pwd`" >out.log
echo "Start Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log

/usr/local/bin/mpirun.lotus $JULES 2>> err.log >> out.log

echo "Post process begin Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log

# create hosts list
rm hosts.txt
export myhosts=($LSB_HOSTS)
for hostName in ${myhosts[*]};do echo $hostName >> hosts.txt ; done

blaunch -u hosts.txt $JOB_RUNNER_DIR/run_scripts/post_process.sh >> out.log 2>> err.log

rm hosts.txt

mv -n processed/* output
rmdir processed

echo "End Time: `date --utc +'%Y-%m-%d %H:%M:%S%z'`" >> out.log
echo "Storage MB: `du -ms`" >> out.log
