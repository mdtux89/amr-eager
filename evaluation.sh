#!/bin/bash

VOCAB_DATASET="/disk/ocean/mdamonte/LDC2015E86/training/deft-p2-amr-r1-amrs-training-all.txt"
SMATCH_PATH="../smatch_2.0.2"
LDC2015E86_dev="/disk/ocean/mdamonte/LDC2015E86/dev/deft-p2-amr-r1-amrs-dev-all.txt"
LDC2015E86_test="/disk/ocean/mdamonte/LDC2015E86/test/deft-p2-amr-r1-amrs-test-all.txt"
#simplesents="examples.txt"
#hand_align="hand_align.txt"

#echo "Collecting resources.."
#python collect.py -t $VOCAB_DATASET > /dev/null

echo "SMATCH SCORES ON DIFFERENT DATASETS"

#echo "LDC2015E86 development set"
#python parser.py -f $LDC2015E86_dev > /dev/null
#python $SMATCH_PATH"/smatch.py" -f "output.txt" $LDC2015E86_dev
#echo ""

echo "LDC2015E86 test set"
#python parser.py -f $LDC2015E86_test > /dev/null
cp $1 out.txt
####cp output.txt out.txt
python $SMATCH_PATH"/smatch.py" -f "out.txt" $LDC2015E86_test
echo ""

#echo "NP-only dataset Smatch"
####python amr-preprocessing/extract_np.py $LDC2015E86_test > "np.txt"	
#python parser.py -f "np.txt.2015" > /dev/null
#python $SMATCH_PATH"/smatch.py" -f $1".np" "np.txt.2015" 
####rm "np.txt"

#echo "Unknown words datasets Smatch"
#####./amr-preprocessing/sents_unk.sh $VOCAB_DATASET $LDC2015E86_test
#for name in `ls $LDC2015E86_test.unk*.out` 
#do 
#       #name=${name::-4}  
#       name=${name::${#name}-4}
#       echo $name
#       python parser.py $name > /dev/null
#       python $SMATCH_PATH"/smatch.py" -f "output.txt" $name
#done

echo "***"

echo ""
echo "ADDITIONAL EVALUATION METRICS ON LDC2015E86 test set"
grep -v "^#" $LDC2015E86_test > $LDC2015E86_test".tmp"
gold=$LDC2015E86_test".tmp"

echo "Unlabeled-arcs Smatch"
sed 's/:[a-zA-Z0-9-]*/:label/g' "out.txt" > 1.tmp
sed 's/:[a-zA-Z0-9-]*/:label/g' $gold > 2.tmp
python $SMATCH_PATH"/smatch.py" -f 1.tmp 2.tmp
echo ""

echo "AMR without WSD Smatch"
cat "out.txt" | perl -ne 's/(\/ [a-zA-Z0-9\-][a-zA-Z0-9\-]*)-[0-9][0-9]*/\1-01/g; print;' > 1.tmp
cat $gold | perl -ne 's/(\/ [a-zA-Z0-9\-][a-zA-Z0-9\-]*)-[0-9][0-9]*/\1-01/g; print;' > 2.tmp
python $SMATCH_PATH"/smatch.py" -f 1.tmp 2.tmp
echo ""

echo "F-score named entities extracted"
python2.7 names_score.py "out.txt" $gold
echo ""

echo "F-score wikis extracted"
python2.7 wiki_score.py "out.txt" $gold
echo ""

echo "F-score concept identification"
python concepts_score.py "out.txt" $gold

echo "F-score reentrancy identification"
python reentrancies_score.py "out.txt" $gold

echo "F-score negation identification"
python polarity_score.py "out.txt" $gold

echo "F-score SRL"
python srl_score.py "out.txt" $gold

echo "F-score alternative to Smatch -- ignoring variable names"
python all_score.py "out.txt" $gold

#rm out.txt
#rm 1.tmp
#rm 2.tmp
#rm output.txt
#rm $LDC2015E86_test.unk*.out
