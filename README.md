# How to run jobs automatically
To add a data set automatically following things are to be done
1. Create a folder with the data set type name
2. Make a new Polly workspace which will run only this data set
3. Create a folder dataset_runs in that folder you can add as much .csv files as required which contains the information to be passed to jobs for running
4. Create a file `sampleJob.json` in the folder which is the file which will contain all the parameters to run the data set conversion as job
5. Create a file `non_secret_env.sh` in the folder. In the file non secret environment common for all the jobs can be added. But by default the following environment variable should be there
```
export WORKSPACE_ID=<workspace-id created for this data set conversion jobs>
export DATASET_COLS="all the coloums of the data set "
export CPU_REQUIRED="CPU in m"
export RAM_REQUIRED="RAM required i Bytes"
```
6. Create a file called `shall_i_run.sh`. In this file you can add some condition which will help run/restrict the jobs from running. For example if you want to run only at night then you can do check for that. Lets say you want to run only one job at a given time that can also be checked here.
