#!/usr/bin/env python
#coding=utf-8

'''
Definition of AMR class. Utility class that interfaces with AMR's API
(https://github.com/nschneid/amr-hackathon) and retrieve variables,
relations and alignments used in the preprocessing script.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

import os
import xml.etree.ElementTree as ET
import src.amr
from collections import defaultdict

class AMR:
	def __init__(self, sentence, amr_string, alignments):
		self.sentence = sentence
		self.amr_string = amr_string
		self.alignments = alignments
		self.relations = []
		self.parsed_amr = src.amr.AMR(self.amr_string)

		self.vars = self.parsed_amr.var2concept()

		v2c = self.parsed_amr.var2concept()
		root_v = str(self.parsed_amr.triples(rel=':top')[0][2])
		root_c = str(self.parsed_amr.triples(head=src.amr.Var(root_v))[0][2])
		self.relations.append(("TOP",":top",root_v))
		# hasparent = {}
		for (var1,label,var2) in self.parsed_amr.role_triples():
			# if str(var2) in hasparent and var2 in self.vars:
			# 	hasparent[str(var2)] = hasparent[str(var2)] + 1
			# 	tmp = str(var2) + "_" + str(hasparent[str(var2)])
			# 	self.vars[tmp] = self.vars[var2]
			# 	var2 = tmp
			# else:
			# 	hasparent[str(var2)] = 1
			self.relations.append((str(var1),str(label),str(var2)))

	def cyclic(self):
		try:
			c = self.parsed_amr.contains_cycle()
		except RuntimeError:
			c = False
		return c

	def getSentence(self):
		return self.sentence

	def toString(self):
		return self.amr_string

	def getVariables(self):
	 	return [(str(k),str(self.vars[k])) for k in self.vars]

	def getRelations(self):
		return [r for r in self.relations if r[0] != r[2]]

	def getAlignments(self):
		return self.alignments