for f in `find split -name 'deft*'`
do
	echo "**"
	echo "FILE "$f
	echo "**"
	echo ""
	#./amr_preprocessing.sh $f
	filename=$(basename $f)
	python2.7 preprocessing.py $filename
done
