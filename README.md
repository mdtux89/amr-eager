# amr-eager

AMR-EAGER [1] is a transition-based parser for Abstract Meaning Representation (http://amr.isi.edu/).

# Installation

- Install the following python dependencies: numpy, nltk, parsimonious and pytorch (github.com/hughperkins/pytorch)
- Run ```./download.sh```

# Run the parser

## Preprocessing:

If input is English sentences (one sentence for line):
- ```./amrpreprocessing/preprocessing.sh -s <sentences_file>```
- ```python amrpreprocessing/preprocessing.py -f <sentences_file>```

If input is unaligned AMR annotation data:
- ```./amrpreprocessing/preprocessing.sh <amr_file>```
- ```python amrpreprocessing/preprocessing.py --amrs -f <amr_file>```

If input is aligned AMR annotation data:
- ```./amrpreprocessing/preprocessing.sh -a <amr_file>```
- ```python amrpreprocessing/preprocessing.py --amrs -f <amr_file>```

## Parsing with pre-trained model
- ```python parser.py -f <file> -m <model_dir>``` (without -m it uses the model provided in the directory ```LDC2015E86```)

# Evaluation

We provide evaluation metrics to compare AMR graphs based on Smatch (http://amr.isi.edu/evaluation.html) and rely on https://github.com/nschneid/amr-hackathon for processing annotations.
evaluation.sh computes a set of metrics between AMR graphs in addition to the traditional Smatch code:

* Unlabeled: Smatch score computed on the predicted graphs after removing all edge labels
* No WSD. Smatch score while ignoring Propbank senses (e.g., duck-01 vs duck-02)
* Named Ent. F-score on the named entity recognition (:name roles)
* Wikification. F-score on the wikification (:wiki roles)
* Negations. F-score on the negation detection (:polarity roles)
* Concepts. F-score on the concept identification task
* Reentrancy. Smatch computed on reentrant edges only
* SRL. Smatch computed on :ARG-i roles only

The different metrics are detailed and explained in [1], which also uses them to evaluate several AMR parsers.

- ```./amrevaluation/evaluation.sh <amr_file>.parsed <amr_file>```

To use the evaluation script with a different parser, provide the other parser's output as the first argument. Note that if the parser's ouput is not compatible with the parsimonious grammar as specified in amrpreprocessing/src/amr.peg, the script will try to automatically fix the problems but it may fail.

# Train a model
- Install JAMR aligner and set path in ```amrpreprocessing/preprocessing.sh```
- Preprocess training and validation AMR annotation data as explained above
- ```python collect.py -t <training_file> -m <model_dir>```
- ```python create_dataset.py -t <training_file> -v <validation_file> -m <model_dir>```
- Train the two neural networks: ```th nnets/model_rels.lua --model_dir <model_dir>```, ```th nnets/model_labels.lua --model_dir <model_dir>``` and ```th nnets/model_labels.lua --model_dir <model_dir>``` (use also --cuda if you want to use GPUs). Then move the ```.dat``` models in ```<model_dir>```
- To evaluate the performance of the neural networks run ``th nnets/report.lua <model_dir>```. 

# References

[1] "An Incremental Parser for Abstract Meaning Representation", Marco Damonte, Shay B. Cohen and Giorgio Satta. In arXiv:1608.06111 (2016). URL: https://arxiv.org/abs/1608.06111
