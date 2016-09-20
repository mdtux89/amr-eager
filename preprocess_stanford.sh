#Call CoreNLP
/afs/inf.ed.ac.uk/user/s13/s1333293/stanford-corenlp-full-2014-08-27/corenlp.sh -file $1 -outputFormat text
mv "$1.out" "tmp.txt"

#Remove last line
head -n -1 "tmp.txt" > "$1.out"
#rm "tmp.txt"
