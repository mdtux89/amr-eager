#!/bin/bash
JAMR="/disk/ocean/public/tools/jamr2016"
TOKENIZER="${JAMR}/tools/cdec/corpus/tokenize-anything.sh"
CORENLP="/afs/inf.ed.ac.uk/user/s13/s1333293/stanford-corenlp-full-2014-08-27/"

if [ "$#" -ne 1 ]; then
    echo "Usage: sent_preprocessing.sh sentences_file"
    exit
fi
filename=$(basename $1)

"${TOKENIZER}" < "$1" > "$filename.sentences"

java -mx6g -cp "$CORENLP/*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props "corenlp.properties" -file "$1.sentences" --outputFormat text -replaceExtension
