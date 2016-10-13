#!/usr/bin/env python
#coding=utf-8

'''
Script used to parse AMR graphs. It can be done either in oracle mode or using
the learned system (data must be preprocessed accordingly: the oracle also needs
gold graph and alignments). Output is written in "output.txt" unless option
--stdout is used. See command line arguments below for more information.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16 
'''

import argparse
import cPickle as pickle
from transition_system import TransitionSystem
import amrpreprocessing.src.amr
import copy
from embs import Embs
from resources import Resources

argparser = argparse.ArgumentParser(description='Process some integers.')
argparser.add_argument("-s", "--stdout", help="Print results on stdout", action='store_true')
argparser.add_argument("-o", "--oracle", help="Run in oracle mode", action='store_true')
argparser.add_argument("-v", "--verbose", help="Print status information", action='store_true')
argparser.add_argument("-f", "--file", help="Input file", required = True)
argparser.add_argument("-m", "--model", help="Model directory", default="LDC2015E86/")
try:
	args = argparser.parse_args()
except:
	argparser.error("Invalid arguments")
	sys.exit(0)

Resources.init_table(args.model, False)

prefix = args.file
if args.stdout == False:
	fw = open(prefix + ".parsed","w")
embs = Embs(args.model)

alltokens = pickle.load(open(prefix + ".tokens.p", "rb"))
alldependencies = pickle.load(open(prefix + ".dependencies.p", "rb"))
if args.oracle:
	allalignments = pickle.load(open(prefix + ".alignments.p", "rb"))
	allrelations = pickle.load(open(prefix + ".relations.p", "rb"))
	allalignlines = open(prefix + ".alignments").read().splitlines()

i = 0
for i in range(0, len(alltokens)):
 	if args.verbose:
 		print "Sentence", (i + 1)
	if args.stdout == False:
		fw.write("# ::snt " + " ".join([t.word for t in alltokens[i]]) + "\n")
		fw.write("# ::id " + str(i) + "\n")
		if args.oracle:
			fw.write("# ::alignments " + allalignlines[i] + "\n")
	else:
	 	print "# ::snt " + " ".join([t.word for t in alltokens[i]])
	 	print "# ::id " + str(i)
	 	if args.oracle:
	 		print "# ::alignments " + allalignlines[i]

	if args.oracle:
		data = (copy.deepcopy(alltokens[i]), copy.deepcopy(alldependencies[i]), copy.deepcopy(allrelations[i]), copy.deepcopy(allalignments[i]))
    		t = TransitionSystem(embs, data, "ORACLETEST", None)
	else:
 		data = (copy.deepcopy(alltokens[i]), copy.deepcopy(alldependencies[i]))
 		t = TransitionSystem(embs, data, "PARSE", args.model)
	
 	triples = t.relations()
 	if triples != []:
 		graph = amrpreprocessing.src.amr.AMR.triples2String(triples)
 		if str(graph).startswith("(") == False:
 			graph = "(tmp / " + str(graph) + ")"
 		if args.stdout == False:
 			fw.write(str(graph) + "\n" + "\n")
 		else:
 			print str(graph)
 			print ""
 	else:
 		if args.stdout == False:
 			fw.write("(v / emptygraph)" + "\n" + "\n")
 		else:
 			print "(v / emptygraph)"
 			print ""
if args.stdout == False:
	fw.close()
