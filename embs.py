#!/usr/bin/env python
#coding=utf-8

'''
Definition of OneHotEncoding class (for named entity sparse representation),
PretrainedEmbs (for pretrained embeddings) and RndInitLearnedEmbs (for random
initialized ones). Embs puts everything together, using the same random seed.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

import re
import string
import random

class OneHotEncoding:
	def __onehot(self, index):
		onehot = [0]*(self.dim)
		onehot[index  - 1] = 1
		return onehot

	def  __init__(self, vocab):
		lines = open(vocab).readlines()
		self.dim = len(lines) + 3
		self.enc = {}
		for counter, line in enumerate(lines):
			self.enc[line.strip()] = self.__onehot(counter + 1)
		self.enc["<TOP>"] = self.__onehot(len(self.enc) + 1)
		self.enc["<NULL>"] = self.__onehot(len(self.enc) + 1)
		self.enc["<UNK>"] = self.__onehot(len(self.enc) + 1)
	def get(self, label):
		assert(label is not None)
		if label == "<TOP>":
		 	return self.enc["<TOP>"]
		if label.startswith("<NULL"):
		 	return self.enc["<NULL>"]
		if label in self.enc:
			return self.enc[label]
		return self.enc["<UNK>"]

class PretrainedEmbs:
	def __init__(self, generate, initializationFileIn, initializationFileOut, dim, unk, root, nullemb, prepr, punct):
		self.prepr = prepr
		self.indexes = {}
		self.initialization = {}
		self.counter = 1
		self.dim = dim
		self.punct = punct
		self.nullemb = nullemb

		if generate:
			fw = open(initializationFileOut, "w")
		for line in open(initializationFileIn).readlines()[2:]: # first two lines are not actual embeddings
			v = line.split()
			word = v[0]
			if self.prepr:
				word = self._preprocess(word)
			self.indexes[word] = self.counter
			if generate:
				fw.write(v[1])
				for i in v[2:]:
					fw.write("," + str(i))
				fw.write("\n")
			self.counter += 1

		self.indexes["<UNK>"] = self.counter
		if generate:
			fw.write(str(unk[0]))
			for i in unk[1:]:
				fw.write("," + str(i))
			fw.write("\n")
		self.counter += 1

		self.indexes["<TOP>"] = self.counter
		if generate:
			fw.write(str(root[0]))
			for i in root[1:]:
				fw.write("," + str(i))
			fw.write("\n")
		self.counter += 1

		self.indexes["<NULL>"] = self.counter
		if generate:
			fw.write(str(nullemb[0]))
			for i in nullemb[1:]:
				fw.write("," + str(i))
			fw.write("\n")
		self.counter += 1

		if punct != None:
			self.indexes["<PUNCT>"] = self.counter
			if generate:
				fw.write(str(punct[0]))
				for i in punct[1:]:
					fw.write("," + str(i))
				fw.write("\n")
			self.counter += 1
		
	def get(self, word):
		assert(word is not None)
		if word == "<TOP>":
			return self.indexes["<TOP>"]
		if word.startswith("<NULL"):
			return self.indexes["<NULL>"]

		if self.prepr:
			word = self._preprocess(word)
		if self.punct != None and word not in self.indexes and word in list(string.punctuation):
			return self.indexes["<PUNCT>"]
		elif word in self.indexes:
			return self.indexes[word]
		else:
			return self.indexes["<UNK>"]

	def _preprocess(self, word):
		if word.startswith('"') and word.endswith('"') and len(word) > 2:
			word = word[1:-1]
		reg = re.compile(".+-[0-9][0-9]")
		word = word.strip().lower()
		if reg.match(word) != None:
			word = word.split("-")[0]
		if re.match("^[0-9]", word) != None:
			word = word[0]
		word = word.replace("0","zero")
		word = word.replace("1","one")
		word = word.replace("2","two")
		word = word.replace("3","three")
		word = word.replace("4","four")
		word = word.replace("5","five")
		word = word.replace("6","six")
		word = word.replace("7","seven")
		word = word.replace("8","eight")
		word = word.replace("9","nine")
		return word

	def get_wpos(self, word, pos):
		assert(word is not None and pos is not None and ((word != "" and pos != "") or (word == "" and pos == "SP")))
		if pos == "<TOP>" and word == "<TOP>":
			return self.indexes["<TOP>"]
		if word.startswith("<NULL") and pos.startswith("<NULL"):
		 	return self.indexes["<NULL>"]

		if self.prepr:
			word = self._preprocess(word)
			pos = self._preprocess(pos)

		if self.punct != None and word not in self.indexes and word in list(string.punctuation):
			return self.indexes["<PUNCT>"]
		elif word in self.indexes:
			return self.indexes[word]
		else:
			if pos in self.indexes:
				return self.indexes[pos]
			return self.indexes["<UNK>"]
		
	def vocabSize(self):
		return self.counter - 1



class RndInitLearnedEmbs:
	def __init__(self, vocab, prepr):
		self.prepr = prepr
		self.indexes = {}
		for counter, line in enumerate(open(vocab)):
			word = line.strip()
			if self.prepr:
				word = self._preprocess(word)
			self.indexes[word] = counter + 1
		self.indexes["<UNK>"] = len(self.indexes) + 1
		self.indexes["<TOP>"] = len(self.indexes) + 1
		self.indexes["<NULL>"] = len(self.indexes) + 1

	def _preprocess(self, word):
		reg = re.compile(".+-[0-9][0-9]")
		word = word.strip().lower()
		if reg.match(word) != None:
			word = word.split("-")[0]
		word = word.replace("0","zero")
		word = word.replace("1","one")
		word = word.replace("2","two")
		word = word.replace("3","three")
		word = word.replace("4","four")
		word = word.replace("5","five")
		word = word.replace("6","six")
		word = word.replace("7","seven")
		word = word.replace("8","eight")
		word = word.replace("9","nine")
		return word

	def get(self, label):
		assert(label is not None and label != "")
		if label == "<TOP>":
			return self.indexes["<TOP>"]
		if label.startswith("<NULL"):
			return self.indexes["<NULL>"]

		if self.prepr:
			label = self._preprocess(label)
		if label not in self.indexes:
			label = "<UNK>"
		return self.indexes[label]
		
	def vocabSize(self):
		return len(self.indexes)

class Embs:

	def __init__(self, model_dir, generate = False):
		random.seed(0)
		punct100 = [float(0.02*random.random())-0.01 for i in xrange(100)]
		unk100 = [float(0.02*random.random())-0.01 for i in xrange(100)]
		root100 = [float(0.02*random.random())-0.01 for i in xrange(100)]

		unk50 = [float(0.02*random.random())-0.01 for i in xrange(50)]
		root50 = [float(0.02*random.random())-0.01 for i in xrange(50)]

		unk10 = [float(0.02*random.random())-0.01 for i in xrange(10)]
		root10 = [float(0.02*random.random())-0.01 for i in xrange(10)]

		null10 = [float(0.02*random.random())-0.01 for i in xrange(10)]
		null50 = [float(0.02*random.random())-0.01 for i in xrange(50)]

		punct50 = [float(0.02*random.random())-0.01 for i in xrange(50)]

		
		self.deps = RndInitLearnedEmbs(model_dir + "/dependencies.txt", False)
		self.pos = PretrainedEmbs(generate, "resources/posvec10.txt","resources/posembs.txt", 10, unk10, root10, null10, False, None)
		self.words = PretrainedEmbs(generate, "resources/wordvec50.txt", "resources/wordembs.txt", 50, unk50, root50, null50, True, punct50)
		self.nes = OneHotEncoding("resources/namedentities.txt")
		self.rels = RndInitLearnedEmbs(model_dir + "/relations.txt", False)
