#!/bin/bash
K=$(polly jobs status --workspace-id $WORKSPACE_ID -y > data.log; cat data.log | grep "RUNNING" | wc -l)
MAX=5
if [ "$K" -gt "$MAX" ]
then
        exit 1
else
        exit 1
fi
