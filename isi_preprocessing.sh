#!/bin/bash
#JAMR="/disk/cohortnas/public/tools/jamr"
CORENLP="/afs/inf.ed.ac.uk/user/s13/s1333293/stanford-corenlp-full-2014-08-27/"

if [ "$#" -ne 1 ]; then
    echo "Usage: isi_preprocessing.sh AMR_annoration_file"
    exit
fi

echo "Extracting AMR graphs.."
cat $1 | grep -v '^#' | sed 's/~e.[0-9,][0-9,]*//g' >> "$1.graphs"

echo "Extracting tokenized sentences and alignments.."
cat $1 | grep '# ::alignments' | sed 's/^# ::alignments //' > "$1.alignments.isi"
cat $1 | grep '# ::tok ' | sed 's/^# ::tok //' > "$1.sentences"

echo "Running CoreNLP.."
java -mx6g -cp "$CORENLP/*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props "corenlp.properties" -file "$1.sentences" --outputFormat text -replaceExtension
rm "$1.sentences"

echo "Done!"
