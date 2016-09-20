#!/usr/bin/env python
#coding=utf-8

'''
Definition of Alignments class. For each sentence, computes the list of node variables that are aligned 
to each index in the sentence, if any. 

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

import src.amr
import re
from collections import defaultdict

class Alignments:

	def _traverse(self, parsed_amr, amr):
		root = re.findall("^\([a-zA-Z0-9]+ / [a-zA-Z0-9]+",amr)[0].split(" ")[0][1:]
		triples =  parsed_amr.triples()
		triples2 = []
		instanced = set()
		for i in range (0, len(triples)):
			rel = triples[i]
			if rel[1] != ":instance-of":
				if rel[2].is_constant() or ((i + 1) < len(triples) and triples[i + 1][0] == rel[2] and triples[i + 1][1] == ":instance-of"):
					triples2.append(rel)
		indexes = {}
		queue = []
		queue.append((root, "0"))

		while len(queue) > 0:
			(node,prefix) = queue.pop(0)
			indexes[prefix] = node
			children = [t[2] for t in triples2 if str(t[0]) == node]
			i = 0
			for c in children:
				c = str(c)
				queue.append((c, prefix + "." + str(i)))
				i += 1
		return indexes

	def __init__(self, alignments_filename, graphs):
		self.alignments = []
		for g, line in zip(graphs,open(alignments_filename)):
			amr = g.strip()
			parsed_amr = src.amr.AMR(amr)
			line = line.strip()
			indexes = self._traverse(parsed_amr, amr)
			al = defaultdict(list)
			if line != "":
				for a in line.split(" "):
					if a.strip() == "":
						continue
					start = a.split("|")[0].split("-")[0]
					if start[0] == "*":
						start = start[1:]
					end = a.split("|")[0].split("-")[1]
					for i in range(int(start),int(end)):
						for segment in a.split("|")[1].split("+"):
							al[i].append(indexes[segment])
			self.alignments.append(al)
