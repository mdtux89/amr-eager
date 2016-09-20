#!/usr/bin/env python
#coding=utf-8

'''
Definition of Stack class. It represents the stack of the transition system as a
list of 'Node'. Only the first item in the list can be accessed. It also stores
the list of AMR 'Relation' objects created so far.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''
from relations import Relations
from node import Node
from buftoken import BufToken
import embs

class Stack:
	def __init__(self, embs):
		root = Node(True)
		self.embs = embs
		self.nodes = [root]
		self.relations = Relations()
		self.pushed_consts = 0

	def __repr__(self):
		stack = []
		for item in self.nodes:
			if item.isRoot:
				stack.append("ROOT")
			else:
				stack.append(item.concept)
		return '<%s %s %s>' % (self.__class__.__name__, stack, self.relations)

	def isEmpty(self):
		return len(self.nodes) == 1

	def push(self, n):
		assert(isinstance(n, Node))
		self.nodes.append(n)

	def pop(self, k = 0):
		if k == 0:
			return self.nodes.pop()
		k = len(self.nodes) - 1 - k
		return self.nodes.pop(k)

	def top(self):
		return self.nodes[len(self.nodes) - 1]

	def swap(self):
		assert(len(self.nodes) >= 3)
		tmp = copy.deepcopy(self.nodes[-2])
		self.nodes[-2] = self.nodes[-3]
		self.nodes[-3] = tmp

	def get(self, K):
		if len(self.nodes) - 1 - K < 0:
			return None
		try:
			return self.nodes[len(self.nodes) - 1 - K]
		except IndexError:
			return None

	def root(self):
		return self.nodes[0]

	def size(self):
		return len(self.nodes)

	def concepts(self, K, start = 0):
		origK = K
		ret = []
		if start < 0:
			for i in range(start, 0):
				ret.append(self.embs.words.get("<NULL>"))
				K-= 1
			start = 0

		nodes = [n for n in self.nodes[::-1][start:(K+start)]]
		for item in nodes:
			if item.isRoot:
				ret.append(self.embs.words.get("<TOP>"))
			elif item.isConst:
				ret.append(self.embs.words.get(item.constant))
			else:
				ret.append(self.embs.words.get(item.concept))

		for i in range(len(ret), origK):
			ret.append(self.embs.words.get("<NULL>"))
		assert(len(ret) == origK)
		return ret

	def words(self, K, start = 0):
		origK = K
		ret = []
		if start < 0:
			for i in range(start, 0):
				ret.append(self.embs.words.get_wpos("<NULL>","<NULLPOS>"))
				K -= 1
			start = 0

		nodes = [n for n in self.nodes[::-1][start:(K+start)]]
		for item in nodes:
			if item.isRoot:
				ret.append(self.embs.words.get_wpos("<TOP>","<TOP>"))
			else:
				ret.append(self.embs.words.get_wpos(item.token.word, item.token.pos))
		for i in range(len(ret), origK):
			ret.append(self.embs.words.get_wpos("<NULL>","<NULLPOS>"))
		assert(len(ret) == origK)
		return ret

	def pos(self, K, start = 0):
		origK = K
		ret = []
		if start < 0:
			for i in range(start, 0):
				ret.append(self.embs.pos.get("<NULLPOS>"))
				K -= 1
			start = 0

		nodes = [n for n in self.nodes[::-1][start:(K+start)]]
		for item in nodes:
			if item.isRoot:
				ret.append(self.embs.pos.get("<TOP>"))
			else:
				ret.append(self.embs.pos.get(item.token.pos))
		for i in range(len(ret), origK):
			ret.append(self.embs.pos.get("<NULLPOS>"))
		assert(len(ret) == origK)
		return ret

	def nes(self, K, start = 0):
		origK = K
		ret = []
		if start < 0:
			for i in range(start, 0):
				ret.extend(self.embs.nes.get("<NULLNE>"))
				K -= 1
			start = 0

		nodes = [n for n in self.nodes[::-1][start:(K+start)]]
		for item in nodes:
			if item.isRoot:
				ret.extend(self.embs.nes.get("<TOP>"))
			else:
				ret.extend(self.embs.nes.get(item.token.ne))

		for i in range(len(ret)/15, origK):
			ret.extend(self.embs.nes.get("<NULLNE>"))

		return ret

	def  __eq__(self, other):
		return other != None and self.nodes == other.nodes and self.relations == other.relations
