#!/usr/bin/env python
#coding=utf-8

'''
Definition of History class. It stores all pairs of {state, action} that the transition system
generated so far.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

class History:
	def __init__(self):
		self.states = []
		self.actions = []
		self.alignments = []

	def add(self, state, action, token):
		self.states.append(state)
		self.actions.append(action)
		if action.name == "shift":
			nodes = []
			for a in action.argv.nodes:
				if a.var is not None:
					nodes.append(a.var)
				else:
					nodes.append(a.constant)
			self.alignments.append((token,nodes))

	def statesactions(self):
		return [(state, action) for state, action in zip (self.states, self.actions)]

	def lastActions(self, K):
		actions = [item.get_id() for item in self.actions[::-1][0:K]]
		for i in range(len(actions),K):
			actions.append(0)
		return actions

