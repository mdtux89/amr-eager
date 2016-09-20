#!/usr/bin/env python
#coding=utf-8

'''
Preprocessing script. Precomputes tokens, lemmas (only for parsing), named entities, pos tags,
dependency arcs as well as AMR relations and alignments (only for training). MWEs are put
together (with underscores) to form a unique token.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

from spacy.en import English, LOCAL_DATA_DIR
import os
import cPickle as pickle
import re
from alignments import Alignments
import sys
from AMR import *
from node import Node
from buftoken import BufToken
import copy

def init():
        print "Initializing dependency parser and POS tagger.."
        data_dir = os.environ.get('SPACY_DATA', LOCAL_DATA_DIR)
        nlp = English(data_dir=data_dir)
	return nlp

def normalize(token):
        if re.match("[0-9]+,[0-9]+", token) != None:
                token = token.replace(",",".")
        return token

# CHANGED. see below
# def parsing(sentfile):
#         nlp = init()
#         alltokens = []
#         alltags = []
#         alldependencies = []
#         allnes = []
#         alllemmas = []
#         sentences = open(sentfile).readlines()
#         for sentence in sentences:
#                 tokens = []
#                 tags = []
#                 dependencies = []
#                 indexes = []
#                 nes = []
#                 lemmas = []
#                 sentence = re.sub(r"(\w+)/(\w+)",r"\1 / \2", sentence)
#                 sentence = nlp(sentence.strip().decode("utf-8"))
#                 i = 0
#                 index = 0
#                 while i < len(sentence):
#                         tok = sentence[i]
#                         indexes.append(tok.idx)
#                         t = normalize(str(tok).strip())
#                         if str(tok.ent_iob) == "3":
#                                 while i + 1 < len(sentence) and str(sentence[i + 1].ent_iob) == "1":
#                                         t += "_" + normalize(str(sentence[i + 1]).strip())
#                                         indexes.append(sentence[i + 1].idx)
#                                         i += 1
#                         token = BufToken(t, tok.lemma_, str(tok.ent_type_), str(tok.tag_), index, None)
#                         tokens.append(token)
#                         i += 1
#                         index += 1
#                 for tok in sentence:
#                         label = str(nlp.vocab.strings[tok.dep]).strip()
#                         dependencies.append((indexes.index(tok.head.idx), indexes.index(tok.idx), label))

#                 assert len(tokens) == len(tags) == len(nes) == len(lemmas)
#                 alltokens.append(tokens)
#                 alldependencies.append(dependencies)

#         pickle.dump(alldependencies, open(sys.argv[1] +".dependencies.p", "wb"))
#         pickle.dump(alltokens, open(sys.argv[1] +".tokens.p", "wb"))
#         print "Done"

def parsing(sentfile, depsfile):
        seen = []
        nlp = init()
        alltokens = []
        alltags = []
        alldependencies = []
        allnes = []
        alllemmas = []
        sentences = open(sentfile).readlines()
        deps = open(depsfile).read().split("\n\n")
        for sentence, depslines in zip(sentences, deps):
                tokens = []
                dependencies = []
                sentence = re.sub(r"(\w+)/(\w+)",r"\1 / \2", sentence)
                sentence = nlp(sentence.strip().decode("utf-8"))
                indexes = [-1]*len(sentence)
                i = 0
                index = 0
                while i < len(sentence):
                        tok = sentence[i]
                        indexes[i] = index
                        t = normalize(str(tok).strip())
                        if str(tok.ent_iob) == "3":
                                while i + 1 < len(sentence) and str(sentence[i + 1].ent_iob) == "1":
                                        t += "_" + normalize(str(sentence[i + 1]).strip())
                                        indexes[i + 1] = index
                                        i += 1
                        token = BufToken(t, tok.lemma_, str(tok.ent_type_), str(tok.tag_), index, None)
                        tokens.append(token)
                        i += 1
                        index += 1
                assert(-1 not in indexes)

                for line in depslines.split("\n"):
                        label = line.split("(")[0]
                        try:
                                a = int(line.split(",")[0].split("-")[-1]) - 1
                                b = int(line.split(")")[0].split("-")[-1]) - 1
                                if a != -1: 
                                        a = indexes[a]
                                if b != -1:
                                        b = indexes[b]
                        except ValueError:
                                continue
                        if a == -1:
                                dependencies.append((tokens[b], 'ROOT', tokens[b]))
                        elif a != b:
                                dependencies.append((tokens[a], label.split("_")[0], tokens[b]))

                alltokens.append(tokens)
                alldependencies.append(dependencies)
        pickle.dump(alldependencies, open(sys.argv[1] +".dependencies.p", "wb"))
        pickle.dump(alltokens, open(sys.argv[1] +".tokens.p", "wb"))
        print "Done"

def training(sentfile, graphfile, alignsfile, depsfile):
        fw = open("resources/relations.txt","w")
	seen = []
        nlp = init()
        alltokens = []
        alltags = []
        alldependencies = []
        allnes = []
        allrelations = []
        allalignments = []
        sentences = open(sentfile).readlines()
        graphs = open(graphfile).read().split("\n\n")
        deps = open(depsfile).read().split("\n\n")
        a = Alignments(alignsfile, graphs)
        alignments = a.alignments
        for sentence, graph, aligns, depslines in zip(sentences, graphs, alignments, deps):
                graph = graph.strip()
                amr = AMR(sentence, graph, aligns)
                relations = []
                aligns2 = defaultdict(list)
                variables = {}
                for v in amr.getVariables():
                        variables[v[0]] = v[1]
                node_dict = {}
                for (v1,label,v2) in amr.getRelations():
			if label not in seen:
                        	fw.write(label + "\n")
				seen.append(label)
                        if v1 == "TOP":
                                n1 = Node(True)
                                if v2 in variables:
                                        n2 = Node(None, v2, variables[v2], False)
                                else:
                                        n2 = Node(None, v2, None, True)
                        elif v1 in variables and variables[v1] not in ["name","percentage-entity","monetary-entity","ordinal-entity"] and label not in [":name",":wiki"]:
                                if v1 in node_dict:
                                        n1 = node_dict[v1]
                                elif v1 in variables:
                                        n1 = Node(None, v1, variables[v1], False)
                                else:
                                        n1 = Node(None, v1, None, True) 
                                if v2 in node_dict:
                                        n2 = node_dict[v2]
                                elif v2 in variables:
                                        n2 = Node(None, v2, variables[v2], False)
                                else:
                                        n2 = Node(None, v2, None, True)
			else:
				continue
                        relations.append((n1,label,n2))
                        node_dict[n1.var] = n1
                        node_dict[n2.var] = n2
                for key in aligns:
                        aligns2[key] = []
                        for a in aligns[key]:
                                if a in node_dict:
                                        aligns2[key].append(node_dict[a])
                tokens = []
                tags = []
                dependencies = []
                nes = []
                align_list = []
                sentence = re.sub(r"(\w+)/(\w+)",r"\1 / \2", sentence)
                sentence = nlp(sentence.strip().decode("utf-8"))
                #indexes = []
                indexes = [-1]*len(sentence)
                i = 0
                index = 0
                while i < len(sentence):
                        tok = sentence[i]
                        #indexes.append([tok.idx]) ... for spacy dependencies
                        indexes[i] = index
                        t = normalize(str(tok).strip())
                        a = []
                        a.extend(aligns2[i])
                        if str(tok.ent_iob) == "3":
                                while i + 1 < len(sentence) and str(sentence[i + 1].ent_iob) == "1":
                                        t += "_" + normalize(str(sentence[i + 1]).strip())
                                        a.extend(aligns2[i + 1])
                                        #indexes[index].append(sentence[i + 1].idx)
                                        indexes[i + 1] = index
                                        i += 1
                        token = BufToken(t, None, str(tok.ent_type_), str(tok.tag_), index, None)
                        tokens.append(token)
                        for node in a:
                                node.token = token
                                if node.concept == None:
                                        node.concept = str(tok.ent_type_)
                                node_dict[node.var] = node
                        align_list.append(a)
                        i += 1
                        index += 1
                assert(-1 not in indexes)

                # for spacy dependencies (NOT USED ANYMORE)
                # for tok in sentence:
                #         label = str(nlp.vocab.strings[tok.dep]).strip()
                #         a = b = None
                #         for i, lst in enumerate(indexes):
                #                 if tok.head.idx in lst:
                #                         a = i
                #                 if tok.idx in lst:
                #                         b = i
                #         assert(a != None and b != None)
                #         if label == "ROOT" or a != b:
                #                 dependencies.append((a, label, b))

                for line in depslines.split("\n"):
                        label = line.split("(")[0]
                        try:
                                a = int(line.split(",")[0].split("-")[-1]) - 1
                                b = int(line.split(")")[0].split("-")[-1]) - 1
                                if a != -1: 
                                        a = indexes[a]
                                if b != -1:
                                        b = indexes[b]
                        except ValueError:
                                continue
                        if a == -1:
                                dependencies.append((tokens[b], 'ROOT', tokens[b]))
                        elif a != b:
                                dependencies.append((tokens[a], label.split("_")[0], tokens[b]))

                alltokens.append(tokens)
                alldependencies.append(dependencies)
                allrelations.append(relations)
                allalignments.append(align_list)
        pickle.dump(alldependencies, open(sys.argv[1] +".dependencies.p", "wb"))
        pickle.dump(alltokens, open(sys.argv[1] +".tokens.p", "wb"))
        pickle.dump(allrelations, open(sys.argv[1] +".relations.p", "wb"))
        pickle.dump(allalignments, open(sys.argv[1] +".alignments.p", "wb"))
        print "Done"

if __name__ == "__main__":
        if len(sys.argv) == 5:
                training(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        elif len(sys.argv) == 3:
                parsing(sys.argv[1], sys.argv[2])
        else:
                print "Wrong number of arguments"
