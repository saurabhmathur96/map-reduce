#!/usr/bin/env bash

#
# Runs two rounds of mapreduce with the output of first being input to second
#

python3 word_count_split.py 3000 1342-0.txt input_data_1/

python3 submit_job.py word_count input_data_1 output_data_1 localhost:8080 localhost:8081 localhost:8082 localhost:8083

python3 fetch_result.py 1 # job_id

python3 submit_job.py word_count output_data_1 output_data_1 localhost:8080 localhost:8081 localhost:8082 localhost:8083

python3 fetch_result.py 2 # job_id