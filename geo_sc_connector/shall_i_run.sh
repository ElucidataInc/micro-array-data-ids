#!/bin/bash

polly jobs status --workspace-id $WORKSPACE_ID -y > jobs.log
NJOBS_RUNNING=$(grep -E  "(RUNNING|PENDING)" jobs.log | wc -l)

if [[ $NJOBS_RUNNING -lt 2 ]];
then
    echo "Less than 2 jobs running. Gonna run"
    exit 0
else
    echo "2 jobs are already running. Gonna wait"
    exit 1
fi