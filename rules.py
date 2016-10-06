#!/usr/bin/env python
#coding=utf-8

'''
Definition of Rules class. It allows to check whether an AMR relation label is legal 
for two given nodes. Rules for ARG roles are handled by looking in Propbank. Rules
for the other roles are handled by hand-written rules.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

import re
from node import Node
class Rules:

	def __init__(self):
		self.args_rules = []
		self.args_rules.append({})
		self.args_rules.append({})
		self.args_rules.append({})
		self.args_rules.append({})
		self.args_rules.append({})
		self.args_rules.append({})

		self.rels_rules = {}

		for line in open("resources/args_rules.txt"):
			self._add(line, "args")

		for line in open("resources/rels_rules.txt"):
			self._add(line, "rels")

		self.allrels = open("resources/relations.txt").read().splitlines()

	def _add(self, line, type):		
		if type == "args":
			fields = line.split(",")
			for i in range(1,len(fields)):
				self.args_rules[i - 1][fields[0].strip()] = int(fields[i].strip())
		else:
			rel,constr = line.split("\t")
			self.rels_rules[rel] = {}
			for c in constr.split(","):
				fields = c.split("=")
				if len(fields) < 2:
					self.rels_rules[rel][c.strip()] = "true"
				else:
					self.rels_rules[rel][fields[0].strip()] = re.compile(fields[1].strip())

	def check(self, node1, node2):
		assert(isinstance(node1, Node) and isinstance(node2, Node))
                if node1.isConst:
                        return [0]*len(self.allrels)
                if node2.isRoot:
                        return [0]*len(self.allrels)

		legals = [-1]*len(self.allrels)
		for i, rel in enumerate(self.allrels):
			if rel.startswith(":ARG"):
				if rel.endswith("-of"):
					if re.match(r'.*-[0-9][0-9]*', node2.concept) is None:
						legals[i] = 0
					else:
						ind = int(rel[-4])
						if len(self.args_rules) > ind and node2.concept in self.args_rules[ind]:
							legals[i] = self.args_rules[ind][node2.concept]
						else:
							legals[i] = 1
				else:
                                        if node1.concept is not None and re.match(".*-[0-9][0-9]*", node1.concept) is None:
                                                legals[i] = 0
					else:
						ind = int(rel[-1])
						if len(self.args_rules) > ind and node1.concept in self.args_rules[ind]:
							legals[i] = self.args_rules[ind][node1.concept]
						else:
							legals[i] = 1
			else:
				legal = True
				if rel in self.rels_rules:
					rules = self.rels_rules[rel]
					if "a" in rules and node1.isRoot == False and rules["a"].match(node1.var) == None:
						legal = False
					if "b" in rules and rules["b"].match(node2.concept) == None:
						legal = False
					if "a_isroot" in rules and rules["a_isroot"] == "true" and node1.isRoot == False:
						legal = False
					if "b_isconst" in rules and rules["b_isconst"] == "true" and node2.isConst == False:
						legal = False
					if "b_const" in rules and node2.isConst == True and rules["b_const"].match(node2.constant) == None:
						legal = False
					if legal:
						if "excl" in rules and rules["excl"] == "true":
							legals = [0]*len(self.allrels)
							legals[i] = 1
							break
						else:
							legals[i] = 1
					else:
						legals[i] = 0
				else:
					legals[i] = 1
		assert(-1 not in legals)
		return legals
