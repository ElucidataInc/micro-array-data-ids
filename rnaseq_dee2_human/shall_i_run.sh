#!/bin/bash
K=$(polly jobs status --workspace-id 6583 > data.log; cat data.log | grep "RUNNING" | wc -l)
MAX=5
if [ "$K" -gt "$MAX" ]
then
        exit 1
else
        exit 1
fi
