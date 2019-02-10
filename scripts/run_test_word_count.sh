#!/usr/bin/env bash

#
# Runs a trivial case of word count for verification
#

mkdir word_count_test_data
echo "a a b b a a b" > word_count_test_data/1.txt 
echo "c a b a a c" > word_count_test_data/2.txt 

python3 submit_job.py word_count word_count_test_data word_count_test_output localhost:8080 localhost:8081 localhost:8082 localhost:8083
python3 fetch_result.py 1