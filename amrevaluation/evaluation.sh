#!/bin/bash

# Evaluation script. Run as: ./evaluation.sh <gold_data> <parsed_data>

out=`python smatch_2.0.2/smatch.py --pr -f "$1" "$2"`
out=($out)
echo 'Smatch -> P: '${out[1]}', R: '${out[3]}', F: '${out[6]} | sed 's/.$//'

sed 's/:[a-zA-Z0-9-]*/:label/g' "$1" > 1.tmp
sed 's/:[a-zA-Z0-9-]*/:label/g' "$2" > 2.tmp
out=`python smatch_2.0.2/smatch.py --pr -f 1.tmp 2.tmp`
out=($out)
echo 'Unlabeled -> P: '${out[1]}', R: '${out[3]}', F: '${out[6]} | sed 's/.$//'

cat "$1" | perl -ne 's/(\/ [a-zA-Z0-9\-][a-zA-Z0-9\-]*)-[0-9][0-9]*/\1-01/g; print;' > 1.tmp
cat "$2" | perl -ne 's/(\/ [a-zA-Z0-9\-][a-zA-Z0-9\-]*)-[0-9][0-9]*/\1-01/g; print;' > 2.tmp
out=`python smatch_2.0.2/smatch.py --pr -f 1.tmp 2.tmp`
out=($out)
echo 'No WSD -> P: '${out[1]}', R: '${out[3]}', F: '${out[6]} | sed 's/.$//'

cat "$1" | perl -ne 's/-(\d+(\.\d+)?)/\1/g; print;' | perl -ne 's/,/\./g; print;' | perl -ne 's/^#.*\n//g; print;' | perl -ne 's/_//g; print;' | perl -ne 's/[0-9]+([a-zA-Z]+)/\1/g; print;' > 1.tmp
cat "$2" | perl -ne 's/-(\d+(\.\d+)?)/\1/g; print;' | perl -ne 's/,/\./g; print;' | perl -ne 's/^#.*\n//g; print;' | perl -ne 's/_//g; print;' | perl -ne 's/[0-9]+([a-zA-Z]+)/\1/g; print;' > 2.tmp

python scores.py "1.tmp" "2.tmp"

rm 1.tmp
rm 2.tmp
