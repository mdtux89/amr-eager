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
from rules import Rules
from relations import Relations
import PyTorch
import PyTorchHelpers
import numpy as np
import copy

Classify = PyTorchHelpers.load_lua_class('nnets/classify.lua', 'Classify')

class TransitionSystem:

	def __init__(self, embs, data, stage, model_dir = None):
		if model_dir is not None:
			self._classify = Classify(model_dir)
			self._labels = [item.strip() for item in open(model_dir + "/relations.txt").read().splitlines()]
		else:
			self._labels = None

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

		self.state = State(embs, relations2, tokens, dependencies, alignments, oracle, hooks, self.variables, stage, Rules(self._labels))
		self.history = History()
		while self.state.isTerminal() == False:
			tok = copy.deepcopy(self.state.buffer.peek())
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
				self.history.add((f_rel, f_lab, f_reentr), action, tok)
			else:
				break
		assert (self.state.stack.isEmpty() == True and self.state.buffer.isEmpty() == True)
		
	def classifier(self):
		digits, words, pos, deps = self.state.rel_features()
		constr = self.state.legal_actions()
		acttype = int(self._classify.action(digits, words, pos, deps, constr))
		assert(acttype > 0 and acttype < 5)

		if acttype == 1:
			sg = self.state.nextSubgraph()
			return Action("shift", sg)

		if acttype == 2:
			reentr_features = self.state.reentr_features()
			siblings = [item[0] for p in self.state.stack.relations.parents[self.state.stack.top()] for item in self.state.stack.relations.children[p[0]] if item[0] != self.state.stack.top()]
			for s, feats in zip(siblings,reentr_features):
				words, pos, deps = feats
				pred = int(self._classify.reentrancy(words, pos, deps))
			 	if pred == 1:
					arg0_idx = 9
					if self.state.legal_rel_labels("reent", (self.state.stack.top(), s))[arg0_idx] == 1:
						return Action("reduce", (s, ":ARG0", None))
				break
			return Action("reduce", None)

		if acttype == 3:
			rel = "larc"
		elif acttype == 4:
			rel = "rarc"
		constr = self.state.legal_rel_labels(rel, 1)
		digits, words, pos, deps = self.state.lab_features()
		pred = int(self._classify.label(digits, words, pos, deps, constr))
		return Action(rel,self._labels[pred - 1])

	def statesactions(self):
		return self.history.statesactions()

	def relations(self):
		return self.state.stack.relations.triples()

        def alignments(self):
                return self.history.alignments

