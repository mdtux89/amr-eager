#!/usr/bin/env python
#coding=utf-8

'''
Definition of State class. It stores all info related to the state of the transition systems:
buffer, stack, and previous (state,action) pairs. It provides methods to get desired feature 
vectors for those components, for training. It updates when an action is applied. 
It also allows the use of specific "hooks" to manually deal with named entities.
The class also provides methods, used during parsing, to decide which actions are allowed
given the current state and which labels can be used to label a given relation (larc/rarc).

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

from buf import Buffer
from stack import Stack
from node import Node
from rules import Rules
from dependencies import Dependencies 
import hooks
import embs
from subgraph import Subgraph
from resources import Resources
from buftoken import BufToken
from variables import Variables
from relations import Relations
import copy
import re
import numpy as np

STACKWIN = 2
BUFWIN = 4

class State:
	def __init__(self, embs, relations, tokens, dependencies, alignments, oracle, hooks, variables, stage, rules):
		self.semicol_gen_and = False
		self.hooks = hooks
		self.variables = variables
		self.buffer = Buffer(embs, tokens, alignments)
		self.embs = embs
		self.stage = stage
		self.dependencies = Dependencies([(self.buffer.tokens[i1],label,self.buffer.tokens[i2]) for (i1,label,i2) in dependencies])
		self.stack = Stack(embs)
		self.oracle = oracle
		self.rules = rules
		if relations is not None:
			self.gold = Relations(copy.deepcopy(relations))
		else:
			self.gold = None

	def isTerminal(self):
		return self.buffer.isEmpty() and self.stack.isEmpty()

	def __repr__(self):
		return '<%s %s %s>' % (self.__class__.__name__, self.stack, self.buffer)

	def nextSubgraph(self):
		token = self.buffer.peek()
		word_pos = token.word + "_" + token.pos
		lemma_pos = token.lemma + "_" + token.pos

		#TRICK FOR SEMICOLONS
		if token.word == ";":
			if self.semicol_gen_and:
				return Subgraph([],[])
			else:
				self.semicol_gen_and = True
				return Subgraph([Node(token, self.variables.nextVar(), "and", False)],[])

		#HOOKS
		if self.hooks and token.ne != "O" and (token.ne == "ORGANIZATION" and word_pos in Resources.phrasetable) == False:
			ret = hooks.run(token, token.word, token.ne, self.variables)

			if ret != False:
				return Subgraph(ret[0],ret[1])

		#ISI LISTS
		# if token.word in Resources.verbalization_list:
		# 	return Resources.verbalization_list[token.word].get(token, self.variables)
		# if token.lemma in Resources.verbalization_list:
		# 	return Resources.verbalization_list[token.lemma].get(token, self.variables)

		#PHRASETABLE
		if word_pos in Resources.phrasetable:
			return Resources.phrasetable[word_pos].get(token, self.variables)
		if lemma_pos in Resources.phrasetable:
			return Resources.phrasetable[lemma_pos].get(token, self.variables)

		#UNKNOWN TOKENS (variables or constants)
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
			return Subgraph([Node(token, v, label, False)],[])

		#UNKNKOWN CONSTANTS
		nodes = []
		token.word = re.sub("[-\/\\\/\(\)]","_",token.word)
		for t in token.word.split("_"):
			if t.replace(".","").isdigit() and t != '""':
				nodes.append(Node(token, t, token.ne, True))
			elif t != "":
				nodes.append(Node(token, '"' + t + '"', token.ne, True))
		return Subgraph(nodes,[])


	def apply(self, action):
		if action.name == "shift":
			token = self.buffer.consume()
			sg = action.argv.get()

			if self.stage == "COLLECT":
				Resources.phrasetable[token.word+"_"+token.pos][action.argv.get(None, Variables())] += 1
				if token.ne == "ORGANIZATION" and token.word not in Resources.seen_org:
					Resources.seen_org.append(token.word)
					Resources.forg.write(token.word)
					for node in sg.nodes:
						if node.isConst == False and node.concept.strip() != "":
							Resources.forg.write(" " + node.concept)
					Resources.forg.write("\n")

			test = []
			for n in sg.nodes:
				if len([r for r in sg.relations if r[1] == n]) == 0: # push only root
					self.stack.push(n)
					test.append(n)
					break

			for n1, n2, label in sg.relations:
			        self.stack.relations.add(n1, n2, label)

		elif action.name == "reduce":
			node = self.stack.pop()
			if action.argv is not None:
				s, label, _ = action.argv
				self.stack.relations.add(node, s, label)

		elif action.name == "larc":
			label = action.argv
			child = self.stack.get(1)
			top = self.stack.top()
			assert (top != None and child != None)

			self.stack.relations.add(top, child, label)
			self.stack.pop(1)

		elif action.name == "rarc":
			label = action.argv
			child = self.stack.get(1)
			top = self.stack.top()
			assert (top != None and child != None)

			self.stack.relations.add(child, top, label)

		else:
			raise ValueError("action not defined")

	def legal_rel_labels(self, rel, k):
		if rel == "reent":
			return self.rules.check(k[0], k[1])
		if rel == "larc":
			node1 = self.stack.top()
			node2 = self.stack.get(k)
		else:
			node2 = self.stack.top()
			node1 = self.stack.get(k)
		return np.array(self.rules.check(node1, node2), dtype=np.uint8)

	def legal_actions(self):
		top = self.stack.top()
		a = []

		#shift
		if self.buffer.isEmpty() == False:
			a.append(1)
		else:
			a.append(0)

		#reduce
		if self.stack.isEmpty() == False and self.stack.relations.isBasterd(top) == False:
			a.append(1)
		else:
			a.append(0)

		#larc
		node = self.stack.get(1)
		if node is None:
			a.append(0)
		elif node == self.stack.root():
			a.append(0) #larc with root is not allowed
		elif top.isConst == True:
			a.append(0) #relations starting at a constant are not allowed
		elif (top in self.stack.relations.children_nodes(node)) or (node in self.stack.relations.children_nodes(top)):
			a.append(0) #relations are not allowed it there's a relation already there between the two nodes
		else:
			a.append(1)

		#rarc
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
		return np.array(a, dtype=np.uint8)

	def rel_features(self):

		#digits
		digits = []
		for k in range(1, STACKWIN):
			node1 = self.stack.top()
			node2 = self.stack.get(k)
			digits.append(self.stack.relations.est_depth(node2))
			digits.append(self.stack.relations.est_depth(node1))
			digits.append(self.stack.relations.est_depth_down(node2))
			digits.append(self.stack.relations.est_depth_down(node1))
			digits.append(len(self.stack.relations.children[node2]))
			digits.append(len(self.stack.relations.parents[node2]))
			digits.append(len(self.stack.relations.children[node1]))
			digits.append(len(self.stack.relations.parents[node1]))
		digits.extend(self.stack.nes(STACKWIN, 0))
		digits.extend(self.buffer.nes(STACKWIN, 0))

		#concepts/words
		words = []
		words.extend(self.stack.concepts(STACKWIN, 0))
		for k in range(1, STACKWIN):
			node1 = self.stack.top()
			node2 = self.stack.get(k)
			words.append(self.embs.words.get(self.stack.relations.leftmost_parent(node1)))
			words.append(self.embs.words.get(self.stack.relations.leftmost_child(node1)))
			words.append(self.embs.words.get(self.stack.relations.leftmost_grandchild(node1)))
			words.append(self.embs.words.get(self.stack.relations.leftmost_parent(node2)))
			words.append(self.embs.words.get(self.stack.relations.leftmost_child(node2)))
			words.append(self.embs.words.get(self.stack.relations.leftmost_grandchild(node2)))
		words.extend(self.stack.words(STACKWIN, 0))
		words.extend(self.buffer.words(STACKWIN, 0))

		#pos
		pos = []
		pos.extend(self.stack.pos(STACKWIN, 0))
		pos.extend(self.buffer.pos(STACKWIN, 0))

		#deps
		deps = []
		for k in range (1,BUFWIN):
			token1 = self.buffer.peek(k)
			node2 = self.stack.top()
			if token1 is None or node2 is None or node2.token is None:
				deps.append(self.embs.deps.get("<NULLDEP>"))
				deps.append(self.embs.deps.get("<NULLDEP>"))
			else:
				deps.append(self.embs.deps.get(self.dependencies.isArc(token1,node2.token,[])))
				deps.append(self.embs.deps.get(self.dependencies.isArc(node2.token,token1,[])))

		for k in range (1,BUFWIN):
			token1 = self.buffer.peek()
			token2 = self.buffer.peek(k)
			if token1 is None or token2 is None:
				deps.append(self.embs.deps.get("<NULLDEP>"))
				deps.append(self.embs.deps.get("<NULLDEP>"))
			else:
				deps.append(self.embs.deps.get(self.dependencies.isArc(token1,token2,[])))
				deps.append(self.embs.deps.get(self.dependencies.isArc(token2,token1,[])))

		for k in range (0,STACKWIN):
			token1 = self.buffer.peek()
			node2 = self.stack.get(k)

			if token1 is None or node2 is None or node2.token is None:
				deps.append(self.embs.deps.get("<NULLDEP>"))
				deps.append(self.embs.deps.get("<NULLDEP>"))
			else:
				deps.append(self.embs.deps.get(self.dependencies.isArc(token1,node2.token,[])))
				deps.append(self.embs.deps.get(self.dependencies.isArc(node2.token,token1,[])))

		for k in range(1, STACKWIN):
			node1 = self.stack.top()
			node2 = self.stack.get(k)
			if node1 is None or node1.token is None or node2 is None or node2.token is None:
				deps.append(self.embs.deps.get("<NULLDEP>"))
				deps.append(self.embs.deps.get("<NULLDEP>"))
			else:
				deps.append(self.embs.deps.get(self.dependencies.isArc(node1.token,node2.token,[])))
				deps.append(self.embs.deps.get(self.dependencies.isArc(node2.token,node1.token,[])))

		return np.array(digits, dtype=np.float64), np.array(words, dtype=np.float64), np.array(pos, dtype=np.float64), np.array(deps, dtype=np.float64)

	def reentr_features(self):
		feats = []

		#extract a different feature vector for each sibling
		for s in [item[0] for p in self.stack.relations.parents[self.stack.top()] for item in self.stack.relations.children[p[0]] if item[0] != self.stack.top()]:
		
			parents = [i[0] for i in self.stack.relations.parents[self.stack.top()]]
			parents = [i[0] for i in self.stack.relations.parents[s] if i[0] in parents]
			parent = parents[0]
			
			#words
			words = []
			words.extend(self.stack.concepts(1, 0))
			if s.isRoot:
				words.append(self.embs.words.get("<TOP>"))
			elif s.isConst:
				words.append(self.embs.words.get(s.constant))
			else:
				words.append(self.embs.words.get(s.concept))

			if parent.isRoot:
				words.append(self.embs.words.get("<TOP>"))
			elif parent.isConst:
				words.append(self.embs.words.get(parent.constant))
			else:
				words.append(self.embs.words.get(parent.concept))

			#pos
			pos = []
			pos.extend(self.stack.pos(1, 0))
			if s.token is not None:
				pos.append(self.embs.pos.get(s.token.pos))
			else:
				pos.append(self.embs.pos.get("<NULLPOS>"))
			if parent.token is not None:
				pos.append(self.embs.pos.get(parent.token.pos))
			else:	
				pos.append(self.embs.pos.get("<NULLPOS>"))


			#deps
			deps = []
			p = self.stack.top()
			if s is not None and s.token is not None and p is not None and p.token is not None:
				deps.append(self.embs.deps.get(self.dependencies.isArc(s.token, p.token,[])))
				deps.append(self.embs.deps.get(self.dependencies.isArc(p.token, s.token,[])))
			else:
				deps.append(self.embs.deps.get("<NULLDEP>"))
				deps.append(self.embs.deps.get("<NULLDEP>"))
			if s is not None and s.token is not None and parent is not None and parent.token is not None:
				deps.append(self.embs.deps.get(self.dependencies.isArc(s.token, parent.token,[])))
				deps.append(self.embs.deps.get(self.dependencies.isArc(parent.token, s.token,[])))
			else:
				deps.append(self.embs.deps.get("<NULLDEP>"))
				deps.append(self.embs.deps.get("<NULLDEP>"))
			if p is not None and p.token is not None and parent is not None and parent.token is not None:
				deps.append(self.embs.deps.get(self.dependencies.isArc(p.token, parent.token,[])))
				deps.append(self.embs.deps.get(self.dependencies.isArc(p.token, parent.token,[])))
			else:
				deps.append(self.embs.deps.get("<NULLDEP>"))
				deps.append(self.embs.deps.get("<NULLDEP>"))

			feats.append((np.array(words, dtype=np.float64), np.array(pos, dtype=np.float64), np.array(deps, dtype=np.float64)))
		return feats

	def lab_features(self):
		node1 = self.stack.top()
		node2 = self.stack.get(1)

		#digits
		digits = []
		digits.append(self.stack.relations.est_depth(node2))
		digits.append(self.stack.relations.est_depth(node1))
		digits.append(self.stack.relations.est_depth_down(node2))
		digits.append(self.stack.relations.est_depth_down(node1))
		digits.append(len(self.stack.relations.children[node2]))
		digits.append(len(self.stack.relations.parents[node2]))
		digits.append(len(self.stack.relations.children[node1]))
		digits.append(len(self.stack.relations.parents[node1]))
		digits.extend(self.stack.nes(2, 0))

		#concepts/words
		words = []
		words.extend(self.stack.concepts(2, 0))
		words.append(self.embs.words.get(self.stack.relations.leftmost_parent(node1)))
		words.append(self.embs.words.get(self.stack.relations.leftmost_child(node1)))
		words.append(self.embs.words.get(self.stack.relations.leftmost_grandchild(node1)))
		words.append(self.embs.words.get(self.stack.relations.leftmost_parent(node2)))
		words.append(self.embs.words.get(self.stack.relations.leftmost_child(node2)))
		words.append(self.embs.words.get(self.stack.relations.leftmost_grandchild(node2)))
		words.extend(self.stack.words(2, 0))

		#pos
		pos = []
		pos.extend(self.stack.pos(2, 0))

		#deps
		deps = []
		if node1 is None or node1.token is None or node2 is None or node2.token is None:
			deps.append(self.embs.deps.get("<NULLDEP>"))
			deps.append(self.embs.deps.get("<NULLDEP>"))
		else:
			deps.append(self.embs.deps.get(self.dependencies.isArc(node1.token, node2.token,[])))
			deps.append(self.embs.deps.get(self.dependencies.isArc(node2.token, node1.token,[])))

		return np.array(digits, dtype=np.float64), np.array(words, dtype=np.float64), np.array(pos, dtype=np.float64), np.array(deps, dtype=np.float64)
