# TinyMapReduce
Assignment 1 for CSCI-B 534

MapReduce in ~1500 lines of Python 3 code.



## Test Cases
The scripts directory contains shell scripts that run MapReduce jobs to test the system.

The scripts directory contains two helper scripts
- `house_party_protocol.sh` spawns 4 worker node servers along with their daemons
- `clean_slate_protocol.sh` kills the workers and their daemons and deletes any files/directories associated MapReduce jobs

To run a test case,
First run
```
$ ./scripts/house_party_protocol.sh
```
The run the test script. And then finally, run
```
$ ./scripts/clean_slate_protocol.sh
```

The test scripts and the directory that the save their results to are as follows:
- `run_inverted_index.sh` saves results in `output_data_2`
- `run_test_inverted_index.sh` saves results in `inverted_index_test_output`
- `run_word_count.sh` saves results in `output_data_1`
- `run_test_word_count.sh` saves results in `word_count_test_output`
- `run_multiple_rounds_word_count.sh` saves results in `output_data_1` (job.1.timestamp.json for round 1 and job.2.timestamp.json for round 2 ie word count of the output of word count)

For example, to run word count
```
$ ./scripts/house_party_protocol.sh
$ ./scripts/run_word_count.sh
```
and to clean-up 
```
$ ./scripts/clean_slate_protocol.sh
```

## Master Interface

The master node is a set of scripts. The scripts and their usage is as follows:
- `initialize_cluster.py` `ipaddress1:port1` `ipaddress2:port2` ...
- `submit_job.py` `job_name` `input_directory`  `output_directory` ipaddress1:port1 ipaddress2:port2 ...
- `destroy_cluster.py` (no parameters)

The master keeps track of jobs in an sqlite database stored in `jobs/local.db`. The `jobs` directory also contains the list of mappers and reducers for each job in JSON files. 

## Jobs

A job is defined by three pieces of code - splitter, mapper and reducer.
- The splitter is executed before submitting a job to the master. For ex. `word_count_split.py`, `inverted_index_split.py`
- The mapper and reducer are the actual job implementations. The are placed in `worker_node/implementations`. Each module defines a type of job and must contain a function named mapper and a function named reducer. For ex. `worker_node/implementations/inverted_index.py`, `worker_node/implementations/word_count.py`

New jobs can be added by adding these three components and updating `worker_node/worker_daemon.py` (around line 104) as described in the comments.


## Worker directory structure

Running `house_party_protocol.sh` or `initialize_cluster.py` will spawn worker processes. Each worker process gets a separate directory with name `worker_directory_i` where i is a number. Each directory contains:
- `rpc_server.pid` and `worker_daemon.pid` - the pid files for the two processes of the worker
- `rpc_server.log` and `worker_daemon.log` - the log file for the two processes of the worker. (The standard output and standard error are redirected to these files)
- `local.db` - the sqlite file for the local database used to keep track of tasks.
- `input.task_name.task_kind.timestamp.json` - these files contain intermediate outputs. Since they are JSON files, they can be read and inspected directly.


## Data flow
1. User wants to run a word count job on 1342-0.txt 
2. User runs the splitting script `word_count_split.py`
3. User runs `initialize_cluster.py` to create worker nodes.
4. User runs `submit_job.py` with the same worker node addresses from (3)
5. `submit_job.py` splits the addresses list such that the first half are made workers and the rest are made reducers. It reads each file in input directory and assigns it to a mapper until all files are assigned. Next it creates a database record and prints the `job_id` associated with that record.
6. Each worker node has an RPC server that is listening for task requests. The servers on the mappers accept the task request and create a database record.
7. The daemon at each worker continuously polls the database for new tasks. When it gets a task, the associated implementation of mapper is called, the results are saved and the database is updated.
8. When a daemon encounters a reduce task, it also receives a list of addresses of mappers and its filter id. It polls each mapper till it has all results associated with its filter id. Now, the associated reducer implementaiton is called. The results are saved and the database is updated.
9. User runs `fetch_result.py` with the `job_id` from (5)
10. `fetch_result.py` reads the associated record from the database and polls the reducer servers for results until it gets all the results. It concatenates all the results and saves them to the output directory.

## Fault Tolerance
Primary fault tolerance mechanism is re-execution of the job. This mechanism was chosen since this was the most convenient. (The assumption here is that the RPC server process will be killed)
### Case 1: A reducer is killed
Now, there is no RPC server listening at that address. So, when the master script `fetch_result.py` tries to make an RPC it gets a `ConnectionError`. This error is caught and the user is asked to re-run the job.

### Case 2: A mapper is killed
Now, there is no RPC server listening at that address. So, when a reducer polls that address, it gets a `ConnectionError`. It sets its result to 0 and saves that in the database. Now, when the master script `fetch_result.py` makes an RPC to the reducer, it gets 0 instead of a list. The script checks for that case and the user is asked to re-run the job.

### Recovery

So, to recover from this, the user would have to destory all nodes and re-initialize the cluster (Ideally using the helper scripts in `scripts/` directory) and then re-submit the job.


## Note
The code was written and tested on Python 3.5.3 on a Debian Linux machine.

The only piece of 3rd party python code that this project uses is `worker_node/daemon.py` which is a class that spawns a daemon process. This project also requires SQLite (Usually all the bindings should be installed along with python)

The data files are from project gutenberg.
