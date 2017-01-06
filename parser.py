#!/usr/bin/env python
#coding=utf-8

'''
Script used to parse sentences into AMR graphs. It can be done either in oracle mode or using
the learned system (data must be preprocessed accordingly: the oracle also needs
gold graph and alignments). See command line arguments below for more information.

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
from collections import defaultdict

def _to_string(triples, root, level, last_child, seen, prefix, indexes, nodes):
    if len(root.split("/")) == 2:
        conc = root.split("/")[1].strip()
    else:
        conc = root.split()[0]
    children = [t for t in triples if str(t[0]) == root.split()[0]]
    if root in seen:
        root = root.split()[0]
        children = []
    else:
        var = root
        if " / " in root:
            var = root.split()[0]
        nodes.append((var,conc))
        indexes[var].append(prefix)
    if " / " in root:
        seen.append(root)
        graph = "(" + root
        if len(children) > 0:
            graph += "\n"
        else:
            graph += ")"
    else:
        graph = root 
    j = 0
    for k, t in enumerate(children):
        if str(t[0]) == root.split()[0]:
            next_r = t[3]
            if t[4] != "":
                next_r += " / " + t[4]
            for i in range(0, level):
                graph += "    "
            seen2 = copy.deepcopy(seen)
            graph += t[2] + " " + _to_string(triples, next_r, level + 1, k == len(children) - 1, seen, prefix + "." + str(j), indexes, nodes)[0]
            if next_r not in seen2 or " / " not in next_r:
                j += 1
    if len(children) > 0:
        graph += ")"
    if not last_child:
        graph += "\n"
    
    return graph, indexes, nodes

def to_string(triples, root):
    children = [t for t in triples if str(t[0]) == root]
    assert(len(children)==1)
    if children[0][4] == "":
	return "(e / emptygraph)", defaultdict(list), []
    return _to_string(triples, children[0][3] + " / " + children[0][4], 1, False, [], "0", defaultdict(list), [])

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
            fw.write("# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "\n(v / emptygraph)\n\n")
            continue

        graph, graph_indexes, nodes = to_string(triples, "TOP")

        graph = graph.strip()
        if str(graph).startswith("(") == False:
            fw.write("# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "\n(v / " + str(graph) + ")\n\n")
            continue

        if args.nodesedges:
            nodesedges = ""
            root = nodes[0][1]
            for n in nodes:
                nodesedges += "# ::node\t" + "+".join(graph_indexes[n[0]]) + "\t" + n[1] + "\n"
            nodesedges += "# ::root\t0\t" + root + "\n"
            for tr in triples:
                if tr[2] == ":top":
                    continue
                nodesedges += "# ::edge\t" + tr[1] + "\t" + tr[2] + "\t" + tr[4] + "\t" + "+".join(graph_indexes[tr[0]]) + "\t" + "+".join(graph_indexes[tr[3]]) + "\n"
            graph = nodesedges + graph
            
        if args.oracle:
            output = "# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "\n# ::alignments " + allalignlines[i] + "\n" + str(graph) + "\n"
        else:
            if args.avoidalignments:
                output = "# ::id " + str(idx) + "\n# ::snt " + " ".join([t for t in ununderscored]) + "\n" + str(graph) + "\n"
            else:
                align_line = ""
                for tok, nodes in t.alignments():
                    if len(nodes) > 0:
                        tmp = align_line
                        align_line += sent_ranges[tok] + "|"
                        for n in nodes:
                            for i in graph_indexes[n]:
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
    argparser.add_argument("-a", "--avoidalignments", help="Doesn't output generated alignments", action='store_true')
    argparser.add_argument("-n", "--nodesedges", help="Outputs nodes and edges in JAMR-like style", action='store_true')
    try:
        args = argparser.parse_args()
    except:
        argparser.error("Invalid arguments")
        sys.exit(0)
    main(args)
