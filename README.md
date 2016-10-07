# amr-preprocessing

Requirements
-------

- JAMR
- CoreNLP

Preproceesing
-------

Open `preprocessing.sh` and change the path for JAMR and CoreNLP. Run `amr_preprocessing.sh <annotationfile>` to extract the AMR graphs from the AMR annotations, run the aligner and the CoreNLP pipeline to extract tokens, pos tags, named entities, lemmas and dependency trees. 

Data extraction
-------

You can then use `amrdata.py` (relies on https://github.com/nschneid/amr-hackathon) to collect information for the annotated sentences:

	from amrdata import *

	data = AMRDataset("test.txt")
	sentindex = 0 # first sentence at index 0
	amr = data.getSent(sentindex)

	print amr.tokens
	print amr.lemmas
	print amr.pos
	print amr.nes

	print amr.graph # the annotation
	print amr.variables # dictionary mapping AMR variables to AMR concepts
	print amr.relations # list of arcs between AMR variables

	print amr.dependencies # list of arcs in the dependency trees
	print amr.alignments # dictionary mapping tokens to AMR variables 

	print amr.amr_api.contains_cycle() # amr_api is a wrapper for https://github.com/nschneid/amr-hackathon

