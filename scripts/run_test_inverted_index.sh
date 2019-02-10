#!/usr/bin/env bash

#
# Runs a trivial case of inverted index for verification
#

mkdir inverted_index_test_data
printf "1\na a b b a a b" > inverted_index_test_data/1.txt 
printf "2\nc a b a a c" > inverted_index_test_data/2.txt 

python3 submit_job.py inverted_index inverted_index_test_data inverted_index_test_output localhost:8080 localhost:8081 localhost:8082 localhost:8083
python3 fetch_result.py 1