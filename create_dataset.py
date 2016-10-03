#!/usr/bin/env python
#coding=utf-8

import cPickle as pickle
from transition_system import TransitionSystem
from embs import Embs
from variables import Variables
from resources import Resources
import sys
import argparse

Resources.init_table(False)

def create(prefix, split, path_datasets):
	print "Loading data.."
	alltokens = pickle.load(open(prefix + ".tokens.p", "rb"))
	alldependencies = pickle.load(open(prefix + ".dependencies.p", "rb"))
	allalignments = pickle.load(open(prefix + ".alignments.p", "rb"))
	allrelations = pickle.load(open(prefix + ".relations.p", "rb"))
	print "Number of sentences ", len(alltokens)

	labels = {}
	labels_counter = 1
	for line in open("resources/relations.txt"):
		labels[line.strip()] = labels_counter
		labels_counter += 1

	# graphlets = {}
	# graphlets_inv = {}
	# gl_counter = 1
	# for line in open("resources/graphlets.txt"):
	# 	graphlets[line.strip()] = gl_counter
	# 	graphlets_inv[gl_counter] = line.strip()
	# 	gl_counter += 1

	dataset = open(path_datasets + "/dataset_"+split+".txt","w")
	labels_dataset = open(path_datasets + "/labels_dataset_"+split+".txt","w")
	# t2s_dataset = open(path_datasets + "/t2s_dataset_"+split+".txt","w")
	reentr_dataset = open(path_datasets + "/reentr_dataset_"+split+".txt","w")

	counter = 0
	embs = Embs()
	for tokens, dependencies, alignments, relations in zip(alltokens, alldependencies, allalignments, allrelations):
		counter += 1
		print "Sentence no: ", counter
		data = (tokens, dependencies, relations, alignments)
		t = TransitionSystem(embs, data, "TRAIN", 0)
		for feats, action in t.statesactions():
			f_rel, f_lab, f_reentr = feats

			for v in f_rel:
				dataset.write(str(v) + ",")
	 		dataset.write(str(action.get_id()) + "\n")

			if action.name.endswith("rel"):
				if action.argv in labels:
					for v in f_lab:
						labels_dataset.write(str(v) + ",")
					labels_dataset.write(str(labels[action.argv]) + "\n")

			# if action.name == "shift":
			# 	gl = action.argv.get(None, Variables())
			# 			t2s_dataset.write(str(v) + ",")	
			# 		t2s_dataset.write(str(graphlets[str(gl)]) + "\n")

			if action.name == "reduce":
			 	if action.argv is not None:
			 		for sib, vec in zip(action.argv[2],f_reentr):
			 			for v in vec:
			 				reentr_dataset.write(str(v) + ",")
			 			if sib == action.argv[0]:
			 				reentr_dataset.write(str(1) + "\n")
			 			else:
			 				reentr_dataset.write(str(2) + "\n")
if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-t", "--train", help="Training set", required = True)
	argparser.add_argument("-v", "--valid", help="Validation set", required = True)
	argparser.add_argument("-o", "--output", help="Output data directory", required = True)

	try:
	    args = argparser.parse_args()
	except:
	    argparser.error("Invalid arguments")
	    sys.exit(0)

	create(args.train, "train", args.output)
	create(args.valid, "valid", args.output)
	print "Done"
