#!/bin/bash
JAMR="/disk/cohortnas/public/tools/jamr"

if [ "$#" -ne 1 ]; then
    echo "Usage: extract_amr_info.sh input_file"
    exit
fi

echo "Extracting sentences, graphs from input file as well as alignments (using JAMR)..."
cat $1 | grep "# ::snt " | sed 's/^# ::snt //' > $1".sentences" 
cat $1 | grep -v '#' > $1".graphs"
. $JAMR/scripts/config.sh
echo "Aligning..."
$JAMR/scripts/ALIGN.sh < $1 | grep '# ::alignments ' | sed 's/^# ::alignments //' | cut -d":" -f1 > $1".alignments"

echo "Done!"
