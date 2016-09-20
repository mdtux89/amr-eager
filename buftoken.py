#!/usr/bin/env python
#coding=utf-8

'''
Definition of BufToken class. It represents a token in the buffer of the transition system.
MWEs should be stored in a single token (taken care during preprocessing). 'nodes' contains
the object of class Nodes this token is aligned to; it contains 'None' if alignments are not
available (no oracle).

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

class BufToken:

	def __init__(self, word, lemma, ne, pos, index, nodes):
		self.word = word
		self.lemma = lemma
		self.ne = ne
		self.pos = pos
		self.index = index
		self.nodes = nodes

	def __eq__(self, other):
		return other != None and self.word == other.word and self.lemma == other.lemma and self.pos == other.pos and self.ne == other.ne and self.index == other.index #and self.nodes == other.nodes

	def __repr__(self):
		return '<%s %s %s %s %s %s %s>' % (
     		self.__class__.__name__, str(self.word), str(self.lemma), self.ne, self.pos, self.index, self.nodes)

	def __hash__(self):
		return hash((self.word, self.lemma, self.ne, self.pos, self.index))
