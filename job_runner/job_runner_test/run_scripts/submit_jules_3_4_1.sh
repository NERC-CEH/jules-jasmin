#!/bin/bash

cat ../../run_scripts/run_in_background_3_4_1.sh > jules_run.sh
chmod +x jules_run.sh
./jules_run.sh 2> submit_err.log > submit_out.log &
PID=$!

echo "Job <$PID> is submitted to default queue <background job>."
