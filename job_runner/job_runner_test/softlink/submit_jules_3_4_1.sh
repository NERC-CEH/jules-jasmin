#!/bin/bash

sh run_in_background_3_4_1.sh 2> submit_err.log > submit_out.log &
PID=$!

echo "Job <$PID> is submitted to default queue <background job>."
