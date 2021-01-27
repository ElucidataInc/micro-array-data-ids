#!/bin/bash

printf "\n" | polly jobs status --workspace-id 6584 >> text.log
NJOBS_RUNNING=$(grep -E  "(RUNNING|PENDING)" text.log | wc -l)

if [[ $NJOBS_RUNNING -lt 3 ]];
then
    echo "Less than 3 jobs running. Gonna run"
    exit 0
else
    echo "2 jobs are already running. Gonna wait"
    exit 1
fi