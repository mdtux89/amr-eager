#!/usr/bin/env python
#coding=utf-8

'''
Preprocessing script. Precomputes tokens, lemmas (only for parsing), named entities, pos tags,
dependency arcs as well as AMR relations and alignments (only for training). MWEs are put
together (with underscores) to form a unique token.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

import cPickle as pickle
import re
from alignments import Alignments
import sys
from AMR import *
from node import Node
from buftoken import BufToken
import copy
import collect

def loadFromFile(stanfordOutput):
	sentences = []
        alltokens = []
        allpos = []
        alllemmas = []
        allnes = []
	alldepslines = []
	blocks = open(stanfordOutput, 'r').read().split("\n\n")
	while True:
		if len(blocks) == 0:
			break
		block = blocks.pop(0).strip().split("\n")
		sentences.append(block[1].strip())
                tokens = [t[5:-1] for t in re.findall('Text=[^\s]* ', block[2])]
                allpos.append([t[13:-1] for t in re.findall('PartOfSpeech=[^\s]* ', block[2])])
                lemmas = [t[6:-1] for t in re.findall('Lemma=[^\s]* ', block[2])]
                nes = [t[15:] for t in re.findall('NamedEntityTag=[^\]]*', block[2])]
                if blocks[0].startswith("\n"):
                        b = ""
                else:
                        b = blocks.pop(0)
		depslines = b
		tokens2 = []
		lemmas2 = []
		nes2 = []
		for token, lemma, ne in zip(tokens, lemmas, nes):
			if len(ne.split()) == 2:
				[name, norm] = ne.split()
				norm = norm[25:]
				tokens2.append(norm)
				lemmas2.append(norm)
				nes2.append(name)
			else:
				tokens2.append(token)
				lemmas2.append(lemma)
				nes2.append(ne.split()[0])
		alltokens.append(tokens2)
		alllemmas.append(lemmas2)
		allnes.append(nes2)
		alldepslines.append(depslines)
	return (sentences, alltokens, allpos, alllemmas, allnes, alldepslines)

def normalize(token):
        if re.match("[0-9]+,[0-9]+", token) != None:
                token = token.replace(",",".")
        return token

def training(prefix):
        allbuftokens = []
        alldependencies = []
        allrelations = []
        allalignments = []
        graphs = open(prefix + ".graphs").read().split("\n\n")
        a = Alignments(prefix + ".alignments", graphs)
        alignments = a.alignments
        sentences, alltokens, allpos, alllemmas, allnes, _ = loadFromFile(prefix + ".corenlp")
	alldepslines = open(prefix + ".deps").read().split("\n\n")
#        seen = []
        k = 0
        print "Number of sentences:", len(sentences)

        #print len(sentences), len(graphs), len(alignments), len(alldepslines), len(alltokens), len(allpos), len(alllemmas), len(allnes)
        for sentence, graph, aligns, depslines, tokens, tags, lemmas, nes in zip(sentences, graphs, alignments, alldepslines, alltokens, allpos, alllemmas, allnes):
                k += 1
                print "Sentence ", k
		#print tokens
		#tokens2 = []
		#for t in tokens:
		#	if t == "'":
		#		tokens2.append("")
		#		tokens2.append("")
		#	else:
		#		tokens2.append(t)
		#	#tokens2.append(t.replace("'",""))
		#print tokens2
		#tokens = tokens2
                graph = graph.strip()
                amr = AMR(sentence, graph, aligns)
                relations = []
                aligns2 = defaultdict(list)
                variables = {}
                for v in amr.getVariables():
                        variables[v[0]] = v[1]
                node_dict = {}
                for (v1,label,v2) in amr.getRelations():
                        # if label not in seen:
                        #         print label
                        #         seen.append(label)
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
    
                for key in aligns:
                        aligns2[key] = []
                        for a in aligns[key]:
                                if a in node_dict and node_dict[a] not in aligns2[key]:
                                        aligns2[key].append(node_dict[a])

                dependencies = []
                align_list = [] 
                buftokens = []
                # sentence = sentence.split()

                #indexes = []
                indexes = [-1]*len(tokens)
                i = 0
                index = 0
                while i < len(tokens):
                        tok = tokens[i]
                        #indexes.append([tok.idx]) #... for spacy dependencies
                        indexes[i] = index
                        t = normalize(str(tok).strip())
                        a = aligns2[i]
                        if nes[i] != "O":
                                while i + 1 < len(tokens) and nes[i + 1] != "O":
                                        t += "_" + normalize(str(tokens[i + 1]).strip())
                                        for item in aligns2[i + 1]:
                                                if item not in a:
                                                        a.append(item)
                                        #indexes[index].append(tokens[i + 1].idx)
                                        indexes[i + 1] = index
                                        i += 1
                        token = BufToken(t, lemmas[i], nes[i], tags[i], index, None)
                        buftokens.append(token)
                        for node in a:
                                node.token = token
                                if node.concept == None:
                                        node.concept = nes[i]
                                        #print node.constant
                                        #node.constant = t
                                        #print node.constant
                                        #raw_input()
                                node_dict[node.var] = node
                        align_list.append(a)
                        i += 1
                        index += 1

		assert(-1 not in indexes)
		#print depslines
		#raw_input()
                for line in depslines.split("\n"):
			#print line
                        pattern = "^(.+)\(.+-([0-9]+), .+-([0-9]+)\)"
                        regex = re.match(pattern, line)
                        if regex is not None:
                                label = regex.group(1)
                                #if label.startswith("prep"):
                                #        label = label.split("_")[0]
                                a = int(regex.group(2)) - 1
                                b = int(regex.group(3)) - 1
                                if a == -1:
                                        dependencies.append((indexes[b], 'ROOT', indexes[b]))
                                elif a != b:
                                        dependencies.append((indexes[a], label, indexes[b]))
                allbuftokens.append(buftokens)
                alldependencies.append(dependencies)
                allrelations.append(relations)
                allalignments.append(align_list)
        pickle.dump(alldependencies, open(prefix +".dependencies.p", "wb"))
        pickle.dump(allbuftokens, open(prefix +".tokens.p", "wb"))
        pickle.dump(allrelations, open(prefix +".relations.p", "wb"))
        pickle.dump(allalignments, open(prefix +".alignments.p", "wb"))
        #### collect.collect(sys.argv[1])
        print "Done"

if __name__ == "__main__":
        if len(sys.argv) == 2:
                parsing(sys.argv[1])
        else:
                print "Wrong number of arguments"
