#!/bin/bash
#CORENLP="/disk/cohortnas/public/tools/stanford-corenlp-full-2014-08-27/"
CORENLP="/disk/ocean/public/tools/stanford-corenlp-full-2015-12-09/"
if [ "$#" -ne 1 ]; then
    echo "Usage: extract_amr_info.sh AMR_annoration_file"
    exit
fi

echo "Extracting AMR graphs.."
cat $1 | grep -v '^#' >> "$1.graphs"

echo "Extracting tokenized sentences and alignments.."
cat $1 | grep '# ::alignments ' | sed 's/^# ::alignments //' | cut -d":" -f1 > "$1.alignments"
cat $1 | grep '# ::tok ' | sed 's/^# ::tok //' > "$1.sentences"

echo "Running CoreNLP.."
java -mx6g -cp "$CORENLP/*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props "corenlp.properties" -file "$1.sentences" --outputFormat text -replaceExtension

echo "Done!"
