#!/bin/bash

./jules_3_4_1.exe 2> err.log > out.log &
PID=$!

echo "Job <$PID> is submitted to default queue <background job>."


