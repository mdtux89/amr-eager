#!/usr/bin/env python
#coding=utf-8

'''
Definition of History class. It stores all pairs of {state, action} that the transition system
generated so far.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''
import copy
class History:
	def __init__(self):
		self.states = []
		self.actions = []
		self.relations = []

	def add(self, state, action, relation):
		self.states.append(state)
		self.actions.append(action)
		if relation != None:
			self.relations.append(relation)

	def statesactions(self):
		return [(state, action) for state, action in zip (self.states, self.actions)]

	def lastRels(self,K):
		relations = copy.deepcopy(self.relations[::-1][0:K])
		for i in range(len(relations),K):
			relations.append("<NULLREL>")
		return relations

	def lastActions(self, K, depth):
		actions = [item.get_id(depth) for item in self.actions[::-1][0:K]]
		for i in range(len(actions),K):
			actions.append(0)
		return actions

