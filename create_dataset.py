#!/usr/bin/env python
#coding=utf-8

'''
Script used to generate the training data from the oracle: D = {state_i, oracle(state_i)}. 
Training and development data must have been preprocessed beforehand with preprocessing.sh and
preprocessing.py. In addition, training data resources must have been collected with collect.py.
Run as: python create_dataset.py -t <training AMR file> -v <dev AMR file> -o <output directory>

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16 
'''

import cPickle as pickle
from transition_system import TransitionSystem
from embs import Embs
from resources import Resources
import sys
import argparse

def create(prefix, split, model_dir):
    print "Loading data.."
    alltokens = pickle.load(open(prefix + ".tokens.p", "rb"))
    alldependencies = pickle.load(open(prefix + ".dependencies.p", "rb"))
    allalignments = pickle.load(open(prefix + ".alignments.p", "rb"))
    allrelations = pickle.load(open(prefix + ".relations.p", "rb"))
    print "Number of sentences ", len(alltokens)

    labels = {}
    labels_counter = 1
    for line in open(model_dir + "/relations.txt"):
        labels[line.strip()] = labels_counter
        labels_counter += 1
    
    dataset = open(model_dir + "/dataset_"+split+".txt","w")
    labels_dataset = open(model_dir + "/labels_dataset_"+split+".txt","w")
    reentr_dataset = open(model_dir + "/reentr_dataset_"+split+".txt","w")

    counter = 0
    embs = Embs(model_dir)
    for tokens, dependencies, alignments, relations in zip(alltokens, alldependencies, allalignments, allrelations):
        counter += 1
        print "Sentence no: ", counter
        data = (tokens, dependencies, relations, alignments)
        t = TransitionSystem(embs, data, "TRAIN")
        for feats, action in t.statesactions():
            f_rel, f_lab, f_reentr = feats

            for f_cat in f_rel:
                for v in f_cat:
                    dataset.write(str(v) + ",")
            dataset.write(str(action.get_id()) + "\n")

            if action.name.endswith("arc"):
                if action.argv in labels:
                    for f_cat in f_lab:
                        for v in f_cat:
                            labels_dataset.write(str(v) + ",")
                    labels_dataset.write(str(labels[action.argv]) + "\n")

            if action.name == "reduce":
                if action.argv is not None:
                    for sib, vec in zip(action.argv[2],f_reentr):
                        for f_cat in vec:
                            for v in f_cat:
                                reentr_dataset.write(str(v) + ",")
                        if sib == action.argv[0]:
                            reentr_dataset.write(str(1) + "\n")
                        else:
                            reentr_dataset.write(str(2) + "\n")
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-t", "--train", help="Training set", required = True)
    argparser.add_argument("-v", "--valid", help="Validation set", required = True)
    argparser.add_argument("-m", "--modeldir", help="Directory used to save the model being trained", required = True)
    try:
        args = argparser.parse_args()
    except:
        argparser.error("Invalid arguments")
        sys.exit(0)

    Resources.init_table(args.modeldir, False)
    create(args.train, "train", args.modeldir)
    create(args.valid, "valid", args.modeldir)
    print "Done"
