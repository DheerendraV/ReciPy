#!/bin/bash

cd ../indexer/  # navigate to crawler directory

echo "Starting BERT indexing. Est. 2.28 hrs till completion. Check data directory for output files"
python3 indexerBERT.py

