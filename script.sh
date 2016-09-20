source /disk/ocean/public/tools/torch/activate.sh
layers=(1 2 3)
units=(100 200 500)

for nlayers in "${layers[@]}"
do
	for nunits in "${units[@]}"
	do
		echo "Testing model: model_"$nlayers"_"$nunits
		python parser.py -f /disk/ocean/mdamonte/deft-p2-amr-r1-amrs-dev-all.txt -m "/disk/ocean/mdamonte/model_dropout/" > /dev/null
		python ../smatch_2.0.2/smatch.py -f output.txt /disk/ocean/mdamonte/deft-p2-amr-r1-amrs-dev-all.txt
	done
done
