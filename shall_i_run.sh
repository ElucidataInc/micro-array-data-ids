#!/bin/bash
if [[ $(date +%u) -gt 5 ]]
then 
  echo "Going to check if the job can be scheduled"
else 
  echo "Normal run"   
    currenttime=$(date +%H:%M)
    echo $currenttime
    if [[ "$currenttime" > "17:00" ]] || [[ "$currenttime" < "12:00" ]]; then
      echo "Going to check if the job can be scheduled"
      exit 0
    else
      echo "It not night to run"
      exit 1
    fi
fi
