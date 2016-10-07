#!/usr/bin/env python
#coding=utf-8

'''
Definition of Resources class. Used inside collect.py, this stores
additional information of the training data such as the 
token-to-subgraph phrasetable, the list of named entities
etc.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

from collections import defaultdict
import cPickle as pickle
import operator
from subgraph import Subgraph
from node import Node
from variables import Variables

class Resources:
	phrasetable = None

	@staticmethod
	def store_table():

		table = {}
		freq = {}
		print "Storing tables.."
		print "Number of tokens:", len(Resources.phrasetable.keys())
		for i, token in enumerate(Resources.phrasetable):
			if i % 100 == 0:
				print "Token:", i
			sg = max(Resources.phrasetable[token].iteritems(), key=operator.itemgetter(1))[0]
			table[token] = sg

		pickle.dump(table, open("resources/phrasetable.p", "wb"))

	@staticmethod
	def init_table(empty = True):
		Resources.phrasetable = defaultdict(lambda : defaultdict(int))

		if empty == False:
			Resources.phrasetable = pickle.load(open("resources/phrasetable.p", "rb"))
		else:
			Resources.seen_ne = []
			Resources.seen_org = []
			Resources.fne = open("resources/namedentities.txt","w")
			Resources.forg = open("resources/organizations.txt","w")

#		Resources.verbalization_list = {}
#		for line in open("resources/verbalization-list-v1.06.txt"):
#			line = line.strip().split()
#			if line[0] == "VERBALIZE":
#				var = Variables()
#				nodes = []
#				ntop = Node(None, var.nextVar(), line[3], False)
#				nodes.append(ntop)
#				relations = []
#				fields = line[4:]
#				for i in range(0,len(fields),2):
#					if fields[i + 1] == "-":
#						n = Node(None, '-', "", True)
#					else:
#						n = Node(None, var.nextVar(), fields[i + 1], False)
#					nodes.append(n)
#					relations.append((ntop,n,fields[i]))
#				Resources.verbalization_list[line[1]] = Subgraph(nodes, relations)
#		for line in open("resources/have-org-role-91-roles-v1.06.txt"):
#			line = line.strip().split()
#			if line[0] == "USE-HAVE-ORG-ROLE-91-ARG2":
#				var = Variables()
#				ntop = Node(None, var.nextVar(), "have-org-role-91", False)
#				node = Node(None, var.nextVar(), line[1], False)
#				Resources.verbalization_list[line[1]] = Subgraph([ntop, node], [(ntop, node, ":ARG2")])
#
#		for line in open("resources/have-rel-role-91-roles-v1.06.txt"):
#			if "#" in line:
#				line = line.split("#")[0]
#			line = line.strip().split()
#			if len(line) > 0 and line[0] == "USE-HAVE-REL-ROLE-91-ARG2":
#				var = Variables()
#				if len(line) >= 3 and line[2] == ":standard":
#					ntop = Node(None, var.nextVar(), "have-rel-role-91", False)
#					node = Node(None, var.nextVar(), line[3], False)
#					Resources.verbalization_list[line[1]] = Subgraph([ntop, node], [(ntop, node, ":ARG2")])
#					Resources.verbalization_list[line[3]] = Subgraph([ntop, node], [(ntop, node, ":ARG2")])
#				else:
#					ntop = Node(None, var.nextVar(), "have-rel-role-91", False)
#					node = Node(None, var.nextVar(), line[1], False)
#					Resources.verbalization_list[line[1]] = Subgraph([ntop, node], [(ntop, node, ":ARG2")])
