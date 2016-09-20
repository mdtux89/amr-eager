DOMAIN="xinhua"
python collect.py -t "/disk/ocean/mdamonte/LDC2015E86/training/deft-p2-amr-r1-amrs-training-$DOMAIN.txt"
for dev in `ls /disk/ocean/mdamonte/LDC2015E86/dev/deft*-dev-*.txt` 
do
	echo "FILE "$dev
	python parser.py -f $dev -m "/disk/ocean/mdamonte/LDC2015E86/nn1_2/$DOMAIN/" > /dev/null
	python ../smatch_2.0.2/smatch.py -f "output.txt" $dev
done
