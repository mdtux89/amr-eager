#!/bin/bash

# Preprocessing script for AMR data
# For preocessing unaligned amr annotations, use: ./preprocessing.sh <file>
# For preprocessing amr annotations aligned with JAMR (or other aligner that generate similar output), use: ./preprocessing.sh -a <file>
# For preprocessing English sentences (parsing only), use: ./preprocessing.sh -s <file>

ALIGNED="0"
SENTS="0"
while [[ $# -gt 1 ]]
do
key="$1"
case $key in
    -a|--aligned)
    ALIGNED="1"
    ;;
    -s|--sents)
    SENTS="1"
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done

if [[ $ALIGNED -eq "0" ]];
then
	JAMR="/disk/ocean/public/tools/jamr2016"
fi
if [[ $SENTS -eq "1" ]];
then
	TOKENIZER="${JAMR}/tools/cdec/corpus/tokenize-anything.sh"
fi
CORENLP="/disk/ocean/public/tools/stanford-corenlp-full-2015-12-09/"

if [ "$#" -ne 1 ]; then
    echo "Usage: preprocessing.sh AMR_annotation_file"
    exit
fi
workdir=$(dirname $1)

if [[ $SENTS -eq "1" ]];
then
	"${TOKENIZER}" < "$1" > "$1.sentences"

else
	echo "Extracting AMR graphs.."
	cat $1 | grep -v '^#' >> "$1.graphs"

	if [[ $ALIGNED -eq "0" ]];
	then
		echo "Running JAMR aligner.."
		source $JAMR/scripts/config.sh
		$JAMR/scripts/ALIGN.sh < "$1" > tmp.txt

		echo "Extracting tokenized sentences and alignments.."
		cat tmp.txt | grep '# ::alignments ' | grep '::annotator Aligner' | sed 's/^# ::alignments //' | cut -d":" -f1 > "$1.alignments"
		cat tmp.txt | grep '# ::tok ' | sed 's/^# ::tok //' > "$1.sentences"
		rm tmp.txt
	else
		echo "Extracting tokenized sentences and alignments.."
		cat $1 | grep '# ::alignments ' | sed 's/^# ::alignments //' | cut -d":" -f1 > "$1.alignments"
		cat $1 | grep '# ::tok ' | sed 's/^# ::tok //' > "$1.sentences"
	fi

fi

echo "Running CoreNLP.."
java -mx6g -cp "$CORENLP/*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props "corenlp.properties" -file "$1.sentences" --outputFormat text -replaceExtension --outputDirectory "$workdir"

echo "Done!"
