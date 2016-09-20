#!/bin/bash

while read input
do
	echo $input > "tmp.txt"
	./sent_preprocessing.sh "tmp.txt" 2> "/dev/null"
	python preprocessing.py -f "tmp.txt" 2> "/dev/null"

	python parser.py --stdout -f "tmp.txt" 
	
done < /dev/stdin
rm "tmp.txt"
