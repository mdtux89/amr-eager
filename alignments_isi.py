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
					triples2.append((rel,False))
				else:
					triples2.append((rel,True))
		indexes = {}
		queue = []
		queue.append((root, False, "1"))
		seen = []
		reentrancies = defaultdict(list)
		while len(queue) > 0:
			(node, r, prefix) = queue.pop(0)
			if node not in seen:
				if r == False:
					indexes[prefix] = node
					seen.append(node)
					children = [(t[2],r) for t,r in triples2 if str(t[0]) == node]
					i = 1
					for c,r in children:
						c = str(c)
						queue.append((c, r, prefix + "." + str(i)))
						i += 1
				else:
					reentrancies[prefix].append(node)
			else:
				reentrancies[prefix].append(node)
		return indexes, reentrancies

	def __init__(self, alignments_filename, graphs):
		self.alignments = []
		for g, line in zip(graphs,open(alignments_filename)):
			amr = g.strip()
			parsed_amr = src.amr.AMR(amr)
			line = line.strip()
			indexes, reentrancies = self._traverse(parsed_amr, amr)
			al = defaultdict(list)
			if line != "":
				for a in line.split(" "):
					if a.strip() == "":
						continue
					[token, node] = a.split("-")
					if node.endswith(".r"):
						continue
					if node in indexes:
						al[int(token)].append(indexes[node])
					elif node in reentrancies:
						al[int(token)].extend(reentrancies[node])
					else:
						assert(False)
			self.alignments.append(al)
