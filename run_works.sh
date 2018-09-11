#! /bin/bash

while true
do
    python mano/worker.py
    seconds=`date +%S`
    sleep `expr 60 - $seconds`
done