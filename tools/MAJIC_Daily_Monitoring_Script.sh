#!/bin/bash

# Script to carry out the daily monitoring on the CEH system

# This script will carry out 6 tasks
# 1. Check the CROWD server is running.
# 2. Check the job runner (server) is up.
# 3. Check the THREDDS map server responds.
# 4. Check the job status updater is working.
# 5. Ensure the database is running.
# 6. Find out the available hard disk space on the server.

## Constants/ Output Variables ##
email="Automated test for CEH MAJIC run on $(date)";
email_list=("misc@tessella.com" "kerg@tessella.com");
error_flag= false;

## Task 1 - CROWD server ##
CROWD_status=`curl -s -o /dev/null -w "%{http_code}" https://crowd.ceh.ac.uk:443/crowd/rest/usermanagement/latest/user`;

if [ CROWD_status != 401 ]; then
    email="$email \n The CROWD server is not responding.";
    error_flag= true;
fi

## Task 2 - Job Runner ##
Job_runner_status=`sudo -u apache curl -s -o /dev/null -w "%{http_code}" -k -H "Content-Type: application/json" -d '[14]' -E /var/local/ssl/majic.crt --key /var/local/ssl/majic.key https://jules-bd1-dev.ceda.ac.uk:8444/jobs/status`;

if [ Job_runner_status != 200 ]; then
    email="$email \n The Job Runner is not responding.";
    error_flag= true;
fi

## Task 3 - The THREDDS Server ##
THREDDS_status=`sudo -u apache curl -s -o /dev/null -w "%{http_code}" -k -E /var/local/ssl/majic.crt --key /var/local/ssl/majic.key https://jules-bd1-dev.ceda.ac.uk:8080/thredds/index.html`;

if [ THREDDS_status != 200 ]; then
    email="$email \n The THREDDS server is not responding.";
    error_flag= true;
fi

## Task 4 - the job status updater ##
# See if the log file has been updated in the last 10 minutes

current_directory=`pwd`;
cd /var/local/majic/logs/;
log_file="cron_job.log";

if [ ! -d "$log_directory" ]; then
    email="$email \n $The Job Runner log file has not been updated in the last 10 minutes.";
    error_flag= true;
else
    # Find the time since the log file was last modified (in seconds).
    time_since_last_modified=`expr $(date +%s) - $(date +%s -r "$log_directory""$log_file")`;
    echo "Time since last modified: $time_since_last_modified"; 
     
    if [ $time_since_last_modified -gt 600 ]; then
       email="$email \n $The Job Runner log file has not been updated in the last 10 minutes.";
       error_flag= true;
    fi
fi    

cd $current_directory
 
## Task 5 - Database ##
mysql_process=`ps aux | grep "/usr/sbin/[m]ysql"`;

if [ "$mysql_process" = "" ]; then
    email="$email \n The local database is not responding.";
    error_flag= true;
fi

## Task 6 - Remaining memory ##
memory=`df -H`;
email="$email \n\n Remaining memory: ${memory}"

## Email support team ##
# Notify the relevant people that the job has run smoothly, or that there is something wrong.
if [ "$error_flag" == false ]; then

    for email_address in "${email_list[@]}"
    do
	echo $email;
        echo $email + "All automated tests passed." | mail -s "Automated Test Passed $(date)" $email_address;
    done
else
    email_list+=("majic.support@tessella.com");
    for email_address in "${email_list[@]}"
    do
	echo $email;
        echo $email + "All automated tests FAILED" | mail -s "Automated Test FAILED $(date)" $email_address;
    done
fi
