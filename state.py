#!/usr/bin/env python
#coding=utf-8

'''
Definition of State class. It stores all info related to the state of the transition systems:
buffer, stack, action history and provides methods to get desired feature vectors for those
components. It also update itself when an action is applied. It also allows the use of specific
"hooks" to manually deal with named entities, which are easily treated with hard written rules.
Different versions of AMR have different behaviours regarding named entities such as cities and
countries: the new version introduces a new ":wiki" relation that wasnt' used previously. To
account gor this, when the field self.hooks is 0 no hooks are allowed; when it is 1 they are
allowed but the ":wiki" relations are not created; for a value greater than 1 ":wiki" relations
are also created.

The class also provides methods to extract features used for parsing as well as methods to decide
which actions are allowed (using simple contraints) at a certain state and which labels can be
used (using hand-written rules) to label a certain relation (in order to help the classifier by
reducing the number of options).

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

from buf import Buffer
from stack import Stack
from node import Node
from rules import Rules
from oracle import Oracle
from dependencies import Dependencies
from droparcs import DropArcs
import hooks
import embs
import cPickle as pickle
#import propbank
from graphlet import Graphlet
from scipy.sparse import coo_matrix
from scipy.sparse import lil_matrix
import numpy as np
import math
from resources import Resources
from buftoken import BufToken
from variables import Variables
from relations import Relations
import copy
import re

class State:
	def __init__(self, embs, relations, depth, tokens, dependencies, alignments, oracle, hooks, variables, stage):
		assert(type(hooks) == int and (oracle == None or isinstance(oracle, Oracle)) and type(depth) == int)
		self.semicol_gen_and = False
		self.prev_gl = None
		self.hooks = hooks
		self.variables = variables
		self.buffer = Buffer(embs, tokens, alignments)
		self.embs = embs
		self.stage = stage
		dependencies2 = [(self.buffer.tokens[i1],label,self.buffer.tokens[i2]) for (i1,label,i2) in dependencies]
		self.dependencies = Dependencies(dependencies2)
		# srl2 = [(self.buffer.tokens[i1],label,self.buffer.tokens[i2]) for (i1,label,i2) in srl]
		# self.srl = Dependencies(srl2)
		self.stack = Stack(embs)
		self.oracle = oracle
		self.rules = Rules()
		self.depth = depth
		if relations is not None:
			self.gold = Relations(copy.deepcopy(relations))
		else:
			self.gold = None
		#self.drop_arcs = DropArcs()
		#self.drops = []

	def isTerminal(self):
		return self.buffer.isEmpty() and self.stack.isEmpty()

	def __repr__(self):
		return '<%s %s %s>' % (self.__class__.__name__, self.stack, self.buffer)


	def oracleGraphlet(self):
		assert(self.gold is not None)
		token = self.buffer.peek()

		#FOR DEBUGGING
		nodes = token.nodes
		relations = []
		flag = False
		for n1 in nodes:
			for n2 in nodes:
				if n1 != n2:
					children_n1 = copy.deepcopy(self.gold.children[n1])
					for (child,label) in children_n1:
						if child == n2 and (n1,n2,label) not in relations:
							relations.append((n1,n2,label))
							# self.gold.children[n1].remove((child,label))
							# self.gold.parents[child].remove((n1,label))
					children_n2 = copy.deepcopy(self.gold.children[n2])
					for (child,label) in children_n2:
						if child == n1 and (n2,n1,label) not in relations:
							relations.append((n2,n1,label))
							# self.gold.children[n2].remove((child,label))
							# self.gold.parents[child].remove((n2,label))

		return Graphlet(nodes, relations)

	def nextGraphlet(self, pred):
		token = self.buffer.peek()
		word_pos = token.word + "_" + token.pos
		lemma_pos = token.lemma + "_" + token.pos

		#TRICK FOR SEMICOLONS
		if token.word == ";":
			if self.semicol_gen_and:
				return Graphlet([],[])
			else:
				self.semicol_gen_and = True
				return Graphlet([Node(token, self.variables.nextVar(), "and", False)],[])

		#HOOKS
		if self.hooks > 0 and token.ne != "O" and (token.ne == "ORGANIZATION" and word_pos in Resources.phrasetable) == False:
			ret = hooks.run(token, token.word, token.ne, self.hooks, self.variables)

			if ret != False:
				return Graphlet(ret[0],ret[1])

                #ISI LISTS
                elif token.word in Resources.verbalization_list:
                        return Resources.verbalization_list[token.word].get(token, self.variables)
                elif token.lemma in Resources.verbalization_list:
                        return Resources.verbalization_list[token.lemma].get(token, self.variables)

		#PHRASETABLE
		if word_pos in Resources.phrasetable:
			#if Resources.tokfreqs[word_pos] >= 5:
			#	return pred.get(token, self.variables)
		 	#else:
			return Resources.phrasetable[word_pos].get(token, self.variables)
		elif lemma_pos in Resources.phrasetable:
			#if Resources.tokfreqs[lemma_pos] >= 5:
			#	return pred.get(token, self.variables)
		 	#else:	
			return Resources.phrasetable[lemma_pos].get(token, self.variables)

		#UNKNOWN (variable or constant)
		if token.ne == "O": #var
			v = self.variables.nextVar()
			label = ""
			if token.pos.startswith("V"):
				label = token.lemma + "-01"
			if label == "":
				label = token.lemma
			if label == "":
				label = token.word
			if label.count('"') % 2 != 0:
				label = "".join(label.rsplit('"', 1))
			if label.count("'") % 2 != 0:
				label = "".join(label.rsplit("'", 1))
			if "_" in label or "\\" in label or ":" in label or "/" in label or "(" in label or ")" in label:
				label = "genericconcept"
			if label == "":
				label = "emptyconcept"
			if label.startswith("@"):
				label = label[1:]
			label = label.lower()
			return Graphlet([Node(token, v, label, False)],[])

		else: # constant (very bad performance but don't know what else to do)
                        nodes = []
                        token.word = re.sub("[-\/\\\/\(\)]","_",token.word)
                        for t in token.word.split("_"):
                                if t.replace(".","").isdigit() and t != '""':
                                        nodes.append(Node(token, t, token.ne, True))
                                elif t != "":
                                        nodes.append(Node(token, '"' + t + '"', token.ne, True))
                        return Graphlet(nodes,[])


	def apply(self, action):
		lastrel = None
		if action.name == "shift":
			token = self.buffer.consume()
			gl = action.argv.get()

			if self.stage == "COLLECT":
				hooks_ret = hooks.run(token, token.word, token.ne, 1, Variables())
				if hooks_ret == False:
					cl_gl = action.argv.get(None, Variables())
					Resources.phrasetable[token.word+"_"+token.pos][cl_gl] += 1
					Resources.seen_gl[str(cl_gl)] += 1
					if Resources.seen_gl[str(cl_gl)] == 5:
						Resources.fgl.write(str(cl_gl) + "\n")
						Resources.list_gl.append(cl_gl)
				if token.ne not in Resources.seen_ne:
					Resources.seen_ne.append(token.ne)
					Resources.fne.write(token.ne + "\n")
				if token.ne == "ORGANIZATION":
					Resources.forg.write(token.word)
				for node in gl.nodes:
					if node.concept is not None and node.concept.strip() != "" and token.ne == "ORGANIZATION":
						if node.constant is None:
							Resources.forg.write(" " + node.concept)
				if token.ne == "ORGANIZATION":
					Resources.forg.write("\n")

			if len(gl.nodes) > 1:
				for n in gl.nodes:
					if len([r for r in gl.relations if r[1] == n]) == 0: # only for root
						self.stack.push(n)
						#for d in self.drops:
						#	self.drop_arcs.add(self.stack.get(1), self.stack.top(), d)
						#self.drops = []
						break

			elif len(gl.nodes) > 0:
 				self.stack.push(gl.nodes[0])
                                #for d in self.drops:
                                #	self.drop_arcs.add(self.stack.get(1), self.stack.top(), d)
 				#self.drops = []

			#else:
				#self.drops.append(token.word)

			for n1, n2, label in gl.relations:
			        self.stack.relations.add(n1, n2, label)
			        n2.isBasterd = False
			return None

		elif action.name == "reduce":
			node = self.stack.pop()
			if action.argv is not None:
				s, label, _ = action.argv
				self.stack.relations.add(node, s, label)

		elif action.name == "lrel":
			label = action.argv
			child = self.stack.get(1)
			top = self.stack.top()
			assert (top != None and child != None)

			lastrel = (top, child, label)
			self.stack.relations.add(top, child, label)
			child.isBasterd = False
			self.stack.pop(1)

		elif action.name == "rrel":
			label = action.argv
			child = self.stack.get(1)
			top = self.stack.top()
			assert (top != None and child != None)

			lastrel = (child, top, label)
			self.stack.relations.add(child, top, label)
			top.isBasterd = False

		else:
			raise ValueError("action not defined")

		return lastrel

	def legal_rel_labels(self, rel, k):
		if rel == "lrel":
			node1 = self.stack.top()
			node2 = self.stack.get(k)
		else:
			node2 = self.stack.top()
			node1 = self.stack.get(k)
		return self.rules.check(node1, node2)

	def legal_actions(self):
		top = self.stack.top()
		a = []

		#shift
		if self.buffer.isEmpty() == False:
			a.append(1)
		else:
			a.append(0)

		#reduce
		if self.stack.isEmpty() == False and top.isBasterd == False:
			a.append(1)
		else:
			a.append(0)

		#lrel
		node = self.stack.get(1)
		if node is None:
			a.append(0)
		elif node == self.stack.root():
			a.append(0) #lrel with root is not allowed
		elif top.isConst == True:
			a.append(0) #relations starting at a constant are not allowed
		elif (top in self.stack.relations.children_nodes(node)) or (node in self.stack.relations.children_nodes(top)):
			a.append(0) #relations are not allowed it there's a relation already there between the two nodes
		else:
			a.append(1)

		#rrel
		node = self.stack.get(1)
		if node is None:
			a.append(0)
		elif node.isConst == True:
			a.append(0) #relations starting at a constant are not allowed
		elif (top in self.stack.relations.children_nodes(node)) or (node in self.stack.relations.children_nodes(top)):
			a.append(0) #relations are not allowed it there's a relation already there between the two nodes
		else:
			a.append(1)

		if 1 not in a and self.stack.isEmpty() == False:
			a[1] = 1
		return a

	def dep_bs(self, index = 0):
		if self.buffer.isEmpty() or self.stack.get(index) is None:
			return self.embs.deps.get("<NULLDEP>")
		a = self.stack.get(index).token
		return self.embs.deps.get(self.dependencies.isArc(self.buffer.tokens[0],a,[]))

	def depinv_bs(self, index = 0):
		if self.buffer.isEmpty() or self.stack.get(index) is None:
			return self.embs.deps.get("<NULLDEP>")
		a = self.stack.get(index).token
		return self.embs.deps.get(self.dependencies.isArc(a,self.buffer.tokens[0],[]))

	# def srl_bs(self, index = 0):
	# 	if self.buffer.isEmpty() or self.stack.get(index) is None:
	# 		return self.embs.srl.get("<NULLDEP>")
	# 	a = self.stack.get(index).token
	# 	return self.embs.srl.get(self.srl.isArc(self.buffer.tokens[0],a,[]))

	# def srlinv_bs(self, index = 0):
	# 	if self.buffer.isEmpty() or self.stack.get(index) is None:
	# 		return self.embs.srl.get("<NULLDEP>")
	# 	a = self.stack.get(index).token
	# 	return self.embs.srl.get(self.srl.isArc(a,self.buffer.tokens[0],[]))

	def dep_s(self, i):
		# assert(i > 0 and i < self.stack.depth + 2)

		if self.stack.get(i) is None:
			return self.embs.deps.get("<NULLDEP>")
		else:
			b = self.stack.get(i).token
		return self.embs.deps.get(self.dependencies.isArc(self.stack.top().token,b,[]))

	def depinv_s(self, i):
		# assert(i > 0 and i < self.stack.depth + 2)

		if self.stack.get(i) is None:
			return self.embs.deps.get("<NULLDEP>")
		else:
			a = self.stack.get(i).token
		return self.embs.deps.get(self.dependencies.isArc(a,self.stack.top().token,[]))

	def num_dep_s(self, i):
		# assert(i > 0 and i < self.stack.depth + 2)

		if self.stack.get(i) is None:
			return 0
		else:
			b = self.stack.get(i).token
		return self.dependencies.nArcs(self.stack.top().token,b,[])

	def num_depinv_s(self, i):
		# assert(i > 0 and i < self.stack.depth + 2)

		if self.stack.get(i) is None:
			return 0
		else:
			a = self.stack.get(i).token
		return self.dependencies.nArcs(a,self.stack.top().token)

	def rel_features(self):
		feats = []

		#digits
		for k in range(1, self.depth):
			node1 = self.stack.top()
			node2 = self.stack.get(k)
			feats.append(self.stack.relations.est_depth(node2))
			feats.append(self.stack.relations.est_depth(node1))
			feats.append(self.stack.relations.est_depth_down(node2))
			feats.append(self.stack.relations.est_depth_down(node1))
			feats.append(len(self.stack.relations.children[node2]))
			feats.append(len(self.stack.relations.parents[node2]))
			feats.append(len(self.stack.relations.children[node1]))
			feats.append(len(self.stack.relations.parents[node1]))
		feats.extend(self.stack.nes(self.depth, 0))
		feats.extend(self.buffer.nes(self.depth, 0))
		# N = 0
		# print len(feats) - N
		# N = len(feats)

		#concepts/words
		feats.extend(self.stack.concepts(self.depth, 0))
		for k in range(1, self.depth):
			node1 = self.stack.top()
			node2 = self.stack.get(k)
			feats.append(self.embs.words.get(self.stack.relations.leftmost_parent_lab(node1)))
			feats.append(self.embs.words.get(self.stack.relations.leftmost_child_lab(node1)))
			feats.append(self.embs.words.get(self.stack.relations.leftmost_grandchild_lab(node1)))
			feats.append(self.embs.words.get(self.stack.relations.leftmost_parent_lab(node2)))
			feats.append(self.embs.words.get(self.stack.relations.leftmost_child_lab(node2)))
			feats.append(self.embs.words.get(self.stack.relations.leftmost_grandchild_lab(node2)))
		feats.extend(self.stack.words(self.depth, 0))
		feats.extend(self.buffer.words(self.depth, 0))

                #node1 = self.stack.get(1)
                #node2 = self.stack.top()
                #if node1 is None or node2 is None:
               # 	feats.append(self.embs.words.get("<NULL>"))
                #        feats.append(self.embs.words.get("<NULL>"))
		#	feats.append(self.embs.words.get("<NULL>"))
                #else:
                #        feats.append(self.embs.words.get(self.drop_arcs.kth_label(node1,node2,0)))
                #        feats.append(self.embs.words.get(self.drop_arcs.kth_label(node1,node2,1)))
		#	feats.append(self.embs.words.get(self.drop_arcs.kth_label(node1,node2,2)))
		# print len(feats) - N
		# N = len(feats)

		#pos
		feats.extend(self.stack.pos(self.depth, 0))
		feats.extend(self.buffer.pos(self.depth, 0))
		# print len(feats) - N
		# N = len(feats)

		#deps
                for k in range (1,4):
                        token1 = self.buffer.peek(k)
                        node2 = self.stack.top()
                        if token1 is None or node2 is None or node2.token is None:
                                feats.append(self.embs.deps.get("<NULLDEP>"))
                                feats.append(self.embs.deps.get("<NULLDEP>"))
                        else:
                                feats.append(self.embs.deps.get(self.dependencies.isArc(token1,node2.token,[])))
                                feats.append(self.embs.deps.get(self.dependencies.isArc(node2.token,token1,[])))

                for k in range (1,4):
                        token1 = self.buffer.peek()
                        token2 = self.buffer.peek(k)
                        if token1 is None or token2 is None:
                                feats.append(self.embs.deps.get("<NULLDEP>"))
                                feats.append(self.embs.deps.get("<NULLDEP>"))
                        else:
                                feats.append(self.embs.deps.get(self.dependencies.isArc(token1,token2,[])))
                                feats.append(self.embs.deps.get(self.dependencies.isArc(token2,token1,[])))

		for k in range (0,self.depth):
			token1 = self.buffer.peek()
			node2 = self.stack.get(k)
			if token1 is None or node2 is None or node2.token is None:
				feats.append(self.embs.deps.get("<NULLDEP>"))
				feats.append(self.embs.deps.get("<NULLDEP>"))
			else:
				feats.append(self.embs.deps.get(self.dependencies.isArc(token1,node2.token,[])))
				feats.append(self.embs.deps.get(self.dependencies.isArc(node2.token,token1,[])))
				
		for k in range(1, self.depth):
			node1 = self.stack.top()
			node2 = self.stack.get(k)
			if node1 is None or node1.token is None or node2 is None or node2.token is None:
				feats.append(self.embs.deps.get("<NULLDEP>"))
				feats.append(self.embs.deps.get("<NULLDEP>"))
			else:
				feats.append(self.embs.deps.get(self.dependencies.isArc(node1.token,node2.token,[])))
				feats.append(self.embs.deps.get(self.dependencies.isArc(node2.token,node1.token,[])))

		# print len(feats) - N
		# raw_input()

		return feats

	# def reentr_features(self):
	# 	feats = []

	# 	for s in [item[0] for p in self.stack.relations.parents[self.stack.top()] for item in self.stack.relations.children[p[0]] if item[0] != self.stack.top()]:
	# 		f = []
	# 		f.extend(self.stack.concepts(1, 0))
	# 		if s.isRoot:
	# 			f.append(self.embs.words.get("<TOP>"))
	# 		elif s.isConst:
	# 			f.append(self.embs.words.get(s.constant))
	# 		else:
	# 			f.append(self.embs.words.get(s.concept))
	# 		father = self.stack.relations.parents[self.stack.top()][0][0]

	# 		if father.isRoot:
	# 			f.append(self.embs.words.get("<TOP>"))
	# 		elif father.isConst:
	# 			f.append(self.embs.words.get(father.constant))
	# 		else:
	# 			f.append(self.embs.words.get(father.concept))
	# 		feats.append(f)
	# 	return feats

	# def gl_features(self):
	# 	feats = []

	# 	#words
	# 	#feats.append(self.buffer.peek().word)
	# 	feats.extend(self.stack.words(self.depth, 0))
	# 	feats.extend(self.buffer.words(self.depth, 0))

	# 	#pos
	# 	feats.extend(self.stack.pos(self.depth, 0))
	# 	feats.extend(self.buffer.pos(self.depth, 0))

	# 	return feats

	def lab_features(self, k):
		node1 = self.stack.top()
		node2 = self.stack.get(k)
		feats = []

		#digits
		feats.append(self.stack.relations.est_depth(node2))
		feats.append(self.stack.relations.est_depth(node1))
		feats.append(self.stack.relations.est_depth_down(node2))
		feats.append(self.stack.relations.est_depth_down(node1))
		feats.append(len(self.stack.relations.children[node2]))
		feats.append(len(self.stack.relations.parents[node2]))
		feats.append(len(self.stack.relations.children[node1]))
		feats.append(len(self.stack.relations.parents[node1]))
		feats.extend(self.stack.nes(1, 0))
		feats.extend(self.stack.nes(1, k))
		#N = 0
		# print len(feats) - N
		# N = len(feats)

		#concepts/words
		feats.extend(self.stack.concepts(1, 0))
		feats.extend(self.stack.concepts(1, k))
		feats.append(self.embs.words.get(self.stack.relations.leftmost_parent_lab(node1)))
		feats.append(self.embs.words.get(self.stack.relations.leftmost_child_lab(node1)))
		feats.append(self.embs.words.get(self.stack.relations.leftmost_grandchild_lab(node1)))
		feats.append(self.embs.words.get(self.stack.relations.leftmost_parent_lab(node2)))
		feats.append(self.embs.words.get(self.stack.relations.leftmost_child_lab(node2)))
		feats.append(self.embs.words.get(self.stack.relations.leftmost_grandchild_lab(node2)))
		feats.extend(self.stack.words(1, 0))
		feats.extend(self.stack.words(1, k))

                #if node1 is None or node2 is None:
                #        feats.append(self.embs.words.get("<NULL>"))
                #        feats.append(self.embs.words.get("<NULL>"))
                #        feats.append(self.embs.words.get("<NULL>"))
                #else:
                #        feats.append(self.embs.words.get(self.drop_arcs.kth_label(node2,node1,0)))
                #        feats.append(self.embs.words.get(self.drop_arcs.kth_label(node2,node1,1)))
                #        feats.append(self.embs.words.get(self.drop_arcs.kth_label(node2,node1,2)))


		# print len(feats) - N
		# N = len(feats)

		#pos
		feats.extend(self.stack.pos(1, 0))
		feats.extend(self.stack.pos(1, k))

		# print len(feats) - N
		# N = len(feats)

		#deps
		if node1 is None or node1.token is None or node2 is None or node2.token is None:
			feats.append(self.embs.deps.get("<NULLDEP>"))
			feats.append(self.embs.deps.get("<NULLDEP>"))
		else:
			feats.append(self.embs.deps.get(self.dependencies.isArc(node1.token,node2.token,[])))
			feats.append(self.embs.deps.get(self.dependencies.isArc(node2.token,node1.token,[])))

		# print len(feats) - N
		# N = len(feats)

		return feats
