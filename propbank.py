#!/usr/bin/env python
#coding=utf-8

'''
Definition of routines to predict the label for a given word and 
its context.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

import cPickle as pickle
from spacy.en import English, LOCAL_DATA_DIR
import os
from collections import defaultdict
from scipy import spatial
import numpy as np

class Example:
	def __init__(self, index, tokens, pos):
		self.tokens = tokens
		self.pos = pos
		self.index = index
		self.vector = []

def sent_emb(embs, win_size, index, tokens, pos):
	t = []
	p = []
	index += win_size
	for i in range(0, win_size):
		t.append("<NULL>")
		p.append("<NULLPOS>")
	t.extend(tokens)
	p.extend(pos)
	for i in range(0, win_size):
		t.append("<NULL>")
		p.append("<NULLPOS>")

	vec = []
	tokens = t[index-2:index+3]
	pos = p[index-2:index+3]
	for t,p in zip(tokens,pos):
		vec.extend(embs.w.get(t,p))
		#vec.append(embs.words.get_wpos(t,p))
	return vec

def propbank_vector():
	print "Reading propbank examples.."
	data_dir = os.environ.get('SPACY_DATA', LOCAL_DATA_DIR)
	nlp = English(data_dir=data_dir)
	frames = defaultdict(list)
	for line in open("resources/propbank.txt"):
		l,e = line.strip().split("|")
		l,s = l.split(".")
		doc = nlp(e.strip().decode("utf-8"))
		tokens = [str(tok) for tok in doc]
		pos = [str(tok.tag_) for tok in doc]
		lemmas = [str(tok.lemma_) for tok in doc]
		if l not in lemmas:
			continue
		ind = lemmas.index(l)
		vec = sent_emb(3, ind, tokens, pos)
		frames[l+"."+s].append(vec)
	pickle.dump(frames, open("resources/propbank.p", "wb"))
	print "Done!"

frames = pickle.load(open("resources/propbank.p", "rb"))

def closest(embs, lemma, index, tokens, pos):
	v1 = sent_emb(embs, 3, index, tokens, pos)
	v1=np.array(v1,dtype=float)
	frames_lemma = [k for k in frames.keys() if k.split(".")[0] == lemma]
	mindist = 1
	minframe = ""
	for key in frames_lemma:
		for v2 in frames[key]:
			v2=np.array(v2,dtype=float)
			dist = spatial.distance.cosine(v1, v2)
			if dist < mindist:
				mindist = dist
				minframe = key
	return minframe.replace(".","-")

def frames_for_lemma(lemma):
	return [k.replace(".","-") for k in frames.keys() if k.split(".")[0] == lemma]
# def closest_test(lemma, index, sentence):
# 	doc = nlp(sentence.strip().decode("utf-8"))
# 	tokens = [str(tok) for tok in doc]
# 	pos = [str(tok.tag_) for tok in doc]
# 	return closest(lemma, index, tokens, pos)
