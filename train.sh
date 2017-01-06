./preprocessing.sh $1
./preprocessing.sh $2
./preprocessing.sh $3

python preprocessing.py --amrs -f $1
python preprocessing.py --amrs -f $2
python preprocessing.py --amrs -f $3

python collect.py -t $1 -m $4
python create_dataset.py -t $1 -v $2 -m $4
