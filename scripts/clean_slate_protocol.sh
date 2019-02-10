#!/usr/bin/env bash

#
# Resets everything by killing workers and removing files
#

rm -rf jobs/
rm -rf input_data_*/
rm -rf output_data_*/
rm -rf word_count_test_data/
rm -rf word_count_test_output/
rm -rf inverted_index_test_data/
rm -rf inverted_index_test_output/

python3 destroy_cluster.py

