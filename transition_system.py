#!/usr/bin/env python
#coding=utf-8

'''
Definition of TransitionSystem class. It initializes the state and provide a method to advance
the state as a result of the application of an action. Actions can be determined either by an
oracle (training and oracle mode parsing) or by a supervised trained classifier (actual parsing).
It also provides a method to return the sequence of {state, action} pairs used to construct the
classifier dataset as well as the relations recovered by the transition system.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

from oracle import Oracle
from state import State
from action import Action
from variables import Variables
from history import History
from node import Node
from relations import Relations

try:
	import lutorpy as lua
	lua.require('nnets/classify')
except:
	print "Cannot load Torch models"

class TransitionSystem:
	@staticmethod
	def load_model(model_dir):
		lua.eval('load_model("' + model_dir + '")')

	def __init__(self, embs, data, stage):
		self.labels = [item.strip() for item in open("resources/relations.txt").read().splitlines()]

		if stage == "ORACLETEST":
			assert(len(data) == 4)
			hooks = False
			tokens, dependencies, relations, alignments = data
			lemmas = None
			relations2 = []
			self.gold = relations
			for r in relations:
				if r[1].startswith(":snt"):
					r2 = (Node(True),":top",r[2])
				else:
					r2 = (r[0],r[1],r[2])
				if (r2[0].token is not None or r2[1] == ":top") and r2[2].token is not None:
					relations2.append(r2)
			oracle = Oracle(relations2)
			self.variables = Variables()

		elif stage == "TRAIN" or stage == "COLLECT":
			assert(len(data) == 4)
			hooks = False
			tokens, dependencies, relations, alignments = data
			lemmas = None
			relations2 = []
			for r in relations:
				if r[1].startswith(":snt"):
					r2 = (Node(True),":top",r[2])
				else:
					r2 = (r[0],r[1],r[2])
				if (r2[0].token != None or r2[1] == ":top") and r2[2].token != None:
					relations2.append(r2)
			oracle = Oracle(relations2)
			self.variables = None

		else: #PARSING
			assert(len(data) == 2)
			hooks = True
			tokens, dependencies = data
			relations2 = None
			alignments = None
			oracle = None
			self.variables = Variables()

		self.state = State(embs, relations2, tokens, dependencies, alignments, oracle, hooks, self.variables, stage)
		self.history = History()

		while self.state.isTerminal() == False:
			if oracle is not None:
				action = oracle.valid_actions(self.state)
			else:
				action = self.classifier()

			if action is not None:
				f_rel = []
				f_lab = []
				f_reentr = []
				if stage == "TRAIN":
					f_rel = self.state.rel_features()
					if action.name== "larc" or action.name == "rarc":
						f_lab = self.state.lab_features()
					if action.name == "reduce":
					 	f_reentr = self.state.reentr_features()

				self.state.apply(action)
				self.history.add((f_rel, f_lab, f_reentr), action)
			else:
				break
		assert (self.state.stack.isEmpty() == True and self.state.buffer.isEmpty() == True)
		
	def classifier(self):
		rel_features = self.state.rel_features()
		rel_inputs = ",".join([str(i) for i in rel_features])
		possible_acttype = self.state.legal_actions()
		possible_acttype = ",".join([str(i) for i in possible_acttype])
		acttype = int(lua.eval('predict("' + rel_inputs + '", "' + possible_acttype + '")'))
		assert(acttype > 0 and acttype < 5)

		if acttype == 1:
			sg = self.state.nextSubgraph()
			return Action("shift", sg)

		if acttype == 2:
			reentr_features = self.state.reentr_features()
			siblings = [item[0] for p in self.state.stack.relations.parents[self.state.stack.top()] for item in self.state.stack.relations.children[p[0]] if item[0] != self.state.stack.top()]
			for s, feats in zip(siblings,reentr_features):
			 	reentr_inputs = ",".join([str(i) for i in feats])
			 	pred = int(lua.eval('predict_reentr("' + reentr_inputs + '")'))
			 	if pred == 1:
					arg0_idx = 9
					if self.state.legal_rel_labels("reent", (self.state.stack.top(), s))[arg0_idx] == 1:
						return Action("reduce", (s, ":ARG0", None))
				break
			return Action("reduce", None)

		if acttype == 3:
			rel = "larc"
			possible_labels = self.state.legal_rel_labels("larc", 1)
			lab_features = self.state.lab_features()

		elif acttype == 4:
			rel = "rarc"
			possible_labels = self.state.legal_rel_labels("rarc", 1)
			lab_features = self.state.lab_features()

		possible_labels = ",".join([str(i) for i in possible_labels])
		lab_inputs = ",".join([str(i) for i in lab_features])
		pred = int(lua.eval('predict_labels("' + lab_inputs + '", "' + possible_labels + '")'))
		return Action(rel,self.labels[pred - 1])

	def statesactions(self):
		return self.history.statesactions()

	def relations(self):
		return self.state.stack.relations.triples()
