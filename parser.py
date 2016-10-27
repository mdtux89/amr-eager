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
import copy
from embs import Embs
from resources import Resources
import sys
import src.amr
from collections import defaultdict

def traverse(triples, graph):
    v2prefix = graph.v2prefix
    indexes = defaultdict(list)
    queue = []
    queue.append(("TOP", ""))
    while len(queue) > 0:
        (node,prefix) = queue.pop(0)
        if node != "TOP":
                if node in v2prefix:
                        if v2prefix[node] not in indexes[node]:
                                indexes[node].append(v2prefix[node])
                else:
                        indexes[node].append(prefix[0:-1])
        children = [t[3] for t in triples if str(t[0]) == node]
        i = 0
        for c in children:
            c = str(c)
            queue.append((c, prefix + str(i) + "."))
            i += 1
    return indexes

def main(args):
	Resources.init_table(args.model, False)

	prefix = args.file
	fw = open(prefix + ".parsed","w")
	sys.stderr.write("Writing file " + prefix + ".parsed ...\n")
	embs = Embs(args.model)

	alltokens = pickle.load(open(prefix + ".tokens.p", "rb"))
	alldependencies = pickle.load(open(prefix + ".dependencies.p", "rb"))
	if args.oracle:
		allalignments = pickle.load(open(prefix + ".alignments.p", "rb"))
		allrelations = pickle.load(open(prefix + ".relations.p", "rb"))
		allalignlines = open(prefix + ".alignments").read().splitlines()

	for idx in range(0, len(alltokens)):
		ununderscored = []
		sent_ranges = {}
		i = 0
		for t in alltokens[idx]:
			units = t.word.split("_")
			sent_ranges[t] = str(i) + "-" + str(i + len(units))
			ununderscored.extend(units)
			i += len(units)
		sys.stderr.write("Sentence " + str((idx + 1)) + ": " + " ".join([t for t in ununderscored]) + "\n")
		
		if args.oracle:
			data = (copy.deepcopy(alltokens[idx]), copy.deepcopy(alldependencies[idx]), copy.deepcopy(allrelations[idx]), copy.deepcopy(allalignments[idx]))
	    		t = TransitionSystem(embs, data, "ORACLETEST", None)	
		else:
			data = (copy.deepcopy(alltokens[idx]), copy.deepcopy(alldependencies[idx]))
			t = TransitionSystem(embs, data, "PARSE", args.model)
		
		triples = t.relations()
		if triples == []:
			fw.write("# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "\n(v / emptygraph)\n")
			continue
	
		graph = src.amr.AMR.triples2String(triples)
		if str(graph).startswith("(") == False:
			fw.write("# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "(v / " + str(graph) + ")\n")
			continue

		if args.oracle:
			output = "# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "\n# ::alignments " + allalignlines[i] + "\n" + str(graph) + "\n"
		else:
			graph_indices = traverse(triples, graph)
			if args.noalign:
				output = "# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "\n" + str(graph) + "\n"
			else:
				align_line = ""
		        	for tok, nodes in t.alignments():
	                	       	if len(nodes) > 0:
						tmp = align_line
	                	               	align_line += sent_ranges[tok] + "|"
	                	               	for n in nodes:
	                	               	        for i in graph_indices[n]:
	                	               	                align_line += i + "+"
						if align_line.endswith("|"):
							align_line = tmp
						else:
	                        	       		align_line = align_line[0:-1] + " "
				output = "# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "\n# ::alignments " + align_line + "\n" + str(graph) + "\n"
		fw.write(output + "\n")
		
	fw.close()

if __name__ == "__main__":
	argparser = argparse.ArgumentParser(description='Process some integers.')
	argparser.add_argument("-o", "--oracle", help="Run in oracle mode", action='store_true')
	argparser.add_argument("-f", "--file", help="Input file", required = True)
	argparser.add_argument("-m", "--model", help="Model directory", default="LDC2015E86/")
	argparser.add_argument("-n", "--noalign", help="Doesn't output generated alignments", action='store_true')
	try:
	        args = argparser.parse_args()
	except:
	        argparser.error("Invalid arguments")
	        sys.exit(0)
	main(args)
