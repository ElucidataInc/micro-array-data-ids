#!/bin/bash
K=$(polly jobs status --workspace-id $WORKSPACE_ID -y > data.log; cat data.log | grep "RUNNING" | wc -l)
MAX=5
if [ "$K" -gt "$MAX" ]
then
        exit 1
else
        exit 0
fi
#if [[ $(date +%u) -gt 5 ]]
#then 
#  echo "Going to check if the job can be scheduled"
#  exit 0
#else 
#  echo "Normal run"   
#    currenttime=$(date +%H:%M)
#    echo $currenttime
#    if [[ "$currenttime" > "17:00" ]] || [[ "$currenttime" < "12:00" ]]; then
#      echo "Going to check if the job can be scheduled"
#      exit 0
#    else
#      echo "Going to check if the job can be scheduled"
#      exit 0
#    fi
#fi
