#!/usr/bin/env python
#coding=utf-8

'''
Definition of Oracle class. Given information related to the gold AMR relations
and the current state (including alignment information), it decides which action
should be taken next.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

from action import Action
from relations import Relations
from node import Node
import copy
import codecs
from collections import defaultdict
import numpy
from graphlet import Graphlet
import cPickle as pickle

class Oracle:

	def reentrancy(self, node, found):
		# siblings = [item[0] for p in found.parents[node] for item in found.children[p[0]] if item[0] != node]
		# for s in siblings:
		# 	label = self.gold.isRel(node, s)
		# 	if label is not None:
		# 		self.gold.parents[s].remove((node,label))
		# 		self.gold.children[node].remove((s,label))
		# 		return [s, label, siblings]
		return None

	def __init__(self, relations):
		self.gold = Relations(copy.deepcopy(relations))

	def valid_actions(self, state):
		top = state.stack.top()

		other = state.stack.get(1)
		label = self.gold.isRel(top, other)
		if label is not None:
			self.gold.children[top].remove((other,label))
			self.gold.parents[other].remove((top,label))
			assert((other,label) not in self.gold.children[top])
			assert((top,label) not in self.gold.parents[other])
			return Action("lrel", label)

		label = self.gold.isRel(other, top)
		if label is not None:
			self.gold.parents[top].remove((other,label))
			self.gold.children[other].remove((top,label))
			assert((top,label) not in self.gold.children[other])
			assert((other,label) not in self.gold.parents[top])
			return Action("rrel", label)

		if state.stack.isEmpty() == False:# and top.isBasterd == False:
			found = False
			for item in state.buffer.tokens:
				for node in item.nodes:
					if self.gold.isRel(top, node) is not None or self.gold.isRel(node, top) is not None:
						found = True
			if found == False:# and len(state.stack.relations.parents[top]) > 0:
				return Action("reduce", self.reentrancy(top, state.stack.relations))

		if state.buffer.isEmpty() == False:
			token = state.buffer.peek()
			nodes = token.nodes
			relations = []
			flag = False
			for n1 in nodes:
				for n2 in nodes:
					if n1 != n2:
						children_n1 = copy.deepcopy(self.gold.children[n1])
						for (child,label) in children_n1:
							if child == n2:
								relations.append((n1,n2,label))
								self.gold.children[n1].remove((child,label))
								self.gold.parents[child].remove((n1,label))
						children_n2 = copy.deepcopy(self.gold.children[n2])
						for (child,label) in children_n2:
							if child == n1:
								relations.append((n2,n1,label))
								self.gold.children[n2].remove((child,label))
								self.gold.parents[child].remove((n2,label))

 			graphlet = Graphlet(nodes, relations)
 			return Action("shift", graphlet)

		return None
