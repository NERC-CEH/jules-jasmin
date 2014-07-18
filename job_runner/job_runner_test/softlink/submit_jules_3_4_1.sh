#!/bin/bash

sh run_in_background_3_4_1.sh 2>> err.log > out.log &
PID=$!

echo "Job <$PID> is submitted to default queue <background job>."
