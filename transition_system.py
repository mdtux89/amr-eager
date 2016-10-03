#!/usr/bin/env python
#coding=utf-8

'''
Definition of TransitionSystem class. It initializes the state and provide a method to advance
the state as a result of the application of an action. Actions can be determined either by an
oracle (training) or by a supervised trained classifier (parsing).
It also provides a method to return the sequence of {state, action} pairs used to construct the
classifier dataset as well as the relations recovered by the transition system.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''
from oracle import Oracle
from state import State
from action import Action
from variables import Variables
from history import History
import copy
from graphlet import Graphlet
import random
from node import Node
from stack import Stack
import cPickle as pickle
from resources import Resources
from relations import Relations
DEPTH = 2
random.seed(0)
try:
	import lupa
	from lupa import LuaRuntime
	lua = LuaRuntime(unpack_returned_tuples=True)
	lua.require('classify')
except:
	print "Cannot load lua"

class TransitionSystem:
	@staticmethod
	def load_model(model_dir):
		lua.eval('load_model("' + model_dir + '")')

	def __init__(self, embs, data, stage, hooks):
		self.labels = [item.strip() for item in open("resources/relations.txt").read().splitlines()]
		self.controlverbs = [item.strip() for item in open("resources/controlverbs.txt").read().splitlines()]
		self.hooks = hooks

		if stage == "ORACLETEST":
			assert(len(data) == 4)
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

		else:
			assert(len(data) == 2)
			tokens, dependencies = data
			relations2 = None
			alignments = None
			oracle = None
			self.variables = Variables()

		assert(type(hooks) == int and hooks >= 0)
		self.state = State(embs, relations2, DEPTH, tokens, dependencies, alignments, oracle, hooks, self.variables, stage)
		self.history = History()
		#self.fail = False
		assert (self.state.stack.isEmpty() == True and self.state.buffer.isEmpty() == False)
		while self.state.isTerminal() == False:
			#print self.state
			if oracle != None:
				action = oracle.valid_actions(self.state)
				#if action.name == "shift":
	 	                #	pred = self.tok2gl()
				#	try:
                    	 	#		gl = (self.state.nextGraphlet(pred)[0].get(self.state.buffer.peek(), Variables()), self.state.nextGraphlet(pred)[1].get(self.state.buffer.peek(), Variables()))
				#	except:
				#		gl = self.state.nextGraphlet(pred).get(self.state.buffer.peek(), Variables())
				#	orac = action.argv.get(self.state.buffer.peek(), Variables())
				#	try:
				#		if len(gl) == 2 and gl[0] == orac and gl[1] != orac:
				#			print gl[0]
				#			print gl[1]
				#			print orac
				#			raw_input()
				#	except:
				#		pass
			else:
				action = self.classifier()

			if action != None:
				#print action
				f_rel = []
				f_lab = []
				# f_gl = []
				f_reentr = []
				if stage == "TRAIN":
					f_rel = self.state.rel_features()
					if action.name== "lrel" or action.name == "rrel":
						f_lab = self.state.lab_features(1)
					# if action.name == "shift":
					# 	f_gl = self.state.gl_features()
					if action.name == "reduce":
					 	f_reentr = self.state.reentr_features()

				lastRel = self.state.apply(action)

				if lastRel != None:
					lastRel = lastRel[2]

				self.history.add((f_rel, f_lab, f_reentr), action, lastRel)
				#raw_input()
			else:
				assert(oracle != None)
				break
		assert (oracle != None or (self.state.stack.isEmpty() == True and self.state.buffer.isEmpty() == True))
		
		#a = self.state.stack.relations.triples()
		#b =  Relations(self.gold).triples()
		#diff = [i for i in list(set(list(set(a) - set(b))) | set(list(set(b) - set(a)))) if i[1] != ":wiki"]
		#if len(diff) != 0:
	#		self.fail = True	

	def tok2gl(self):
		gl_features = self.state.gl_features()
		gl_inputs = ",".join([str(i) for i in gl_features])
		pred = int(lua.eval('predict_gl("' + gl_inputs + '")'))
		assert(pred != 0)
		return Resources.graphlets[pred - 1]

	def classifier(self):
		rel_features = self.state.rel_features()
		rel_inputs = ",".join([str(i) for i in rel_features])
		possible_acttype = self.state.legal_actions()
		possible_acttype = ",".join([str(i) for i in possible_acttype])
		acttype = int(lua.eval('predict("' + rel_inputs + '", "' + possible_acttype + '")'))

		if acttype == 0:
			return None
		if acttype == 1:
			#t = self.state.buffer.peek()
			#gl = self.state.nextGraphlet()
			pred = ""#self.tok2gl()
			gl = self.state.nextGraphlet(pred)
			return Action("shift", gl)
		if acttype == 2:
			reentr_features = self.state.reentr_features()
			for s, feats in zip([item[0] for p in self.state.stack.relations.parents[self.state.stack.top()] for item in self.state.stack.relations.children[p[0]] if item[0] != self.state.stack.top()],reentr_features):
        	                parents = [i[0].concept for i in self.state.stack.relations.parents[self.state.stack.top()]]
	                        parents = [i[0].concept for i in self.state.stack.relations.parents[s] if i[0].concept in parents]
				#if len([p for p in parents if p is not None and p.split("-")[0] in self.controlverbs]) > 0:
			 	reentr_inputs = ",".join([str(i) for i in feats])
			 	pred = int(lua.eval('predict_reentr("' + reentr_inputs + '")'))
			 	if pred == 1:
					arg0_idx = 9
					if self.state.legal_rel_labels("reent", (self.state.stack.top(), s))[arg0_idx] == 1:
						print self.state.legal_rel_labels("reent", (self.state.stack.top(), s))
						print self.state.stack.top(), s
						return Action("reduce", (s, ":ARG0", None))
				break
			return Action("reduce", None)
		if acttype == 3:
			rel = "lrel"
			possible_labels = self.state.legal_rel_labels("lrel", 1)
			lab_features = self.state.lab_features(1)
		elif acttype == 4:
			rel = "rrel"
			possible_labels = self.state.legal_rel_labels("rrel", 1)
			lab_features = self.state.lab_features(1)

		possible_labels = ",".join([str(i) for i in possible_labels])
		lab_inputs = ",".join([str(i) for i in lab_features])
		pred = int(lua.eval('predict_labels("' + lab_inputs + '", "' + possible_labels + '")'))
		assert(pred != 0)
		return Action(rel,self.labels[pred - 1])

	def statesactions(self):
		return self.history.statesactions()

	def relations(self):
		return self.state.stack.relations.triples()
