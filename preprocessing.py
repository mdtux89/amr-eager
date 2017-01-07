#!/usr/bin/env python
#coding=utf-8

'''
Using the information retrieved by preprocessing.sh, it creates an AMRDataset
instance and generate the pickled object used in collect.py (another preprocessing
step), create_dataset.py (creation of the dataset for training) and parser.py 
(the parser). It can be used to preprocess sentences to be parsed or AMR annotation 
files to train the system or to run in oracle mode (--amrs).

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 3-10-16
'''

import argparse
from amrdata import *
import cPickle as pickle
from node import Node
from buftoken import BufToken
import sys
from collections import defaultdict

negation_words = open("resources/negations.txt").read().splitlines()
negation_words = [n.split()[0].replace('"',"") for n in negation_words]

def normalize(token):
    if re.match("[0-9]+,[0-9]+", token) is not None:
        token = token.replace(",",".")
    return token

def run(prefix, amrs):
    data = AMRDataset(prefix, amrs)
    alltokens = []
    alldependencies = []
    allrelations = []
    allalignments = []
    k = 0
    for i_s, sentence in enumerate(data.getAllSents()):
        print "Sentence", i_s + 1
        k += 1
        if amrs:
            variables = {}
            relations = []
            for v in sentence.variables:
                variables[v[0]] = v[1]
            node_dict = {}
            for (v1,label,v2) in sentence.relations:
                if v1 in node_dict:
                    n1 = node_dict[v1]
                elif v1 == "TOP":
                    n1 = Node(True)
                    node_dict[n1.var] = n1
                elif v1 in variables:
                    n1 = Node(None, v1, variables[v1], False)
                    node_dict[n1.var] = n1
                else:
                    n1 = Node(None, v1, None, True)
                    node_dict[n1.constant] = n1
                if v2 in node_dict:
                    n2 = node_dict[v2]
                elif v2 in variables:
                    n2 = Node(None, v2, variables[v2], False)
                    node_dict[n2.var] = n2
                else:
                    n2 = Node(None, v2, None, True)
                    node_dict[n2.constant] = n2
                relations.append((n1,label,n2))
            aligns = defaultdict(list)
            for key in sentence.alignments:
                aligns[key] = []
                for a in sentence.alignments[key]:
                    if a in node_dict:
                        aligns[key].append(node_dict[a])
        buftokens = []
        indexes = [-1]*len(sentence.tokens)
        i = 0
        index = 0
        align_list = []
        while i < len(sentence.tokens):
            tok = sentence.tokens[i]

            indexes[i] = index
            t = normalize(str(tok).strip())
            if amrs:
                a = aligns[i]

            lst_ne = ["O","DATE","DURATION","SET","TIME"]
            if sentence.nes[i] not in lst_ne:
                while i + 1 < len(sentence.tokens) and sentence.nes[i + 1] == sentence.nes[i]: 
                    t += "_" + normalize(str(sentence.tokens[i + 1]).strip())
                    if amrs:
                        for item in aligns[i + 1]:
                            if item not in a:
                                a.append(item)
                    indexes[i + 1] = index
                    i += 1

            elif sentence.nes[i] == "DATE" and tok.replace("-","").isdigit():
                while i + 1 < len(sentence.tokens) and sentence.nes[i + 1] == sentence.nes[i]:
                    if amrs:
                        for item in aligns[i + 1]:
                            if item not in a:
                                a.append(item)
                    indexes[i + 1] = index
                    i += 1
            token = BufToken(t, sentence.lemmas[i], sentence.nes[i], sentence.pos[i], index, None)
            buftokens.append(token)

            if amrs:
                for node in a:
                    node.token = token
                    if node.concept is None:
                        node.concept = sentence.nes[i]
                    node_dict[node.var] = node
                align_list.append(a)
            i += 1
            index += 1
        dependencies = []
        for d in sentence.dependencies:
            dependencies.append((indexes[d[0]], d[1], indexes[d[2]]))
        assert(-1 not in indexes)

        for tok, al in zip(buftokens, align_list):
            if tok.word in negation_words and al != []:
                neg = Node(tok, "-", None, True)
                neg.concept = "O"
                if neg not in al and tok.word not in [node.concept for node in al]:
                        al.append(neg)
            if tok.word == "not" or tok.word == "n't":
                neg = Node(tok, "-", None, True)
                neg.concept = "O"
                if neg not in al:
                    al.append(neg)
                    
        alltokens.append(buftokens)
        alldependencies.append(dependencies)
        if amrs:
            allrelations.append(relations)
            allalignments.append(align_list)

    pickle.dump(alldependencies, open(prefix +".dependencies.p", "wb"))
    pickle.dump(alltokens, open(prefix +".tokens.p", "wb"))
    if amrs:
        pickle.dump(allrelations, open(prefix +".relations.p", "wb"))
        pickle.dump(allalignments, open(prefix +".alignments.p", "wb"))

if __name__ == "__main__":

        argparser = argparse.ArgumentParser(description='Process some integers.')
        argparser.add_argument("-a", "--amrs", help="Preprocess AMRs (for training) rather than sentences (for testing)", action='store_true')
        argparser.add_argument("-f", "--file", help="Input file", required = True)
        try:
            args = argparser.parse_args()
        except:
            argparser.error("Invalid arguments")
            sys.exit(0)
        run(args.file, args.amrs)
