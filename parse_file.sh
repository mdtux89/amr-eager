#!/bin/bash

echo "Preprocessing.."
./sent_preprocessing.sh $1
python preprocessing.py -f $1

echo "Parsing.."
python parser.py -f $1 -r "output.txt"
