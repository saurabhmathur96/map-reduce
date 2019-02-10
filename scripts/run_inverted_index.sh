#!/usr/bin/env bash

#
# Runs an inverted index job
#

python3 inverted_index_split.py 3000 inverted_index_data/ input_data_2

python3 submit_job.py inverted_index input_data_2 output_data_2 localhost:8080 localhost:8081 localhost:8082 localhost:8083

python3 fetch_result.py 1 # job_id