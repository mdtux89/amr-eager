# amr-eager

AMR-EAGER [1] is a transition-based parser for Abstract Meaning Representation (http://amr.isi.edu/).

[1] "An Incremental Parser for Abstract Meaning Representation", Marco Damonte, Shay B. Cohen and Giorgio Satta. In arXiv:1608.06111 (2016). URL: https://arxiv.org/abs/1608.06111

# Installation

- Install the following python dependencies: nltk, parsimonious, lutorpy
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
- ```python parser.py -f <file> -o <model_dir>``` (without -o it uses the model provided in the directory ```LDC2015E86```)

## Evaluation

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

To use the evaluation script with a different parser, provide the other parser's output as the first argument.

## Train a model

- Preprocess training and validation AMR annotation data as explained above
- ```python collect.py -t <training_file> -o <model_dir>```
- ```python create_dataset.py -t <training_file> -v <validation_file> -o <model_dir>```
- Train the two neural networks: ```th model_rels.lua``` and ```th model_labels.lua``` and save the ```.dat``` models in ```<model_dir>```
