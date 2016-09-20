#!/bin/bash
JAMR="/disk/ocean/public/tools/jamr2016"
#JAMR="/disk/cohortnas/public/tools/jamr"
#CORENLP="/disk/cohortnas/public/tools/stanford-corenlp-full-2014-08-27/"
CORENLP="/disk/ocean/public/tools/stanford-corenlp-full-2015-12-09/"

if [ "$#" -ne 1 ]; then
    echo "Usage: amr_preprocessing.sh AMR_annotation_file"
    exit
fi
filename=$(basename $1)

echo "Extracting AMR graphs.."
cat $1 | grep -v '^#' >> "$filename.graphs"

echo "Running JAMR aligner.."
source $JAMR/scripts/config.sh
$JAMR/scripts/ALIGN.sh < "$1" > tmp.txt

echo "Extracting tokenized sentences and alignments.."
cat tmp.txt | grep '# ::alignments ' | grep '::annotator Aligner' | sed 's/^# ::alignments //' | cut -d":" -f1 > "$filename.alignments"
cat tmp.txt | grep '# ::tok ' | sed 's/^# ::tok //' > "$filename.sentences"
#rm tmp.txt

echo "Running CoreNLP.."
java -mx6g -cp "$CORENLP/*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props "corenlp.properties" -file "$filename.sentences" --outputFormat text -replaceExtension

echo "Done!"
