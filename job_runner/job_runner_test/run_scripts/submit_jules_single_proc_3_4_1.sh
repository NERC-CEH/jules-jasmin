#!/bin/bash

echo "SINGLE PROC" > out.log

cat $1/run_in_background_3_4_1.sh > jules_run.sh

sh jules_run.sh 2> submit_err.log > submit_out.log &
PID=$!

echo "Job <$PID> is submitted to default queue <background job>."
