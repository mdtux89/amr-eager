#!/usr/bin/env python
#coding=utf-8

'''
Definition of Relations class. It stores the graph constructed so far.
It provides a DFS method that is used to retrieve the triples, which in turn are used in src/AMR.py to 
output the AMR graph. 

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

from collections import defaultdict
from node import Node
import copy

class Relations:

	def __init__(self, initial = []):
		self.children = defaultdict(list)
		self.parents = defaultdict(list)
		self.list = []

		for (n1, label, n2) in initial:
			self.add(n1, n2, label)

	def __eq__(self, other):
		return self.children == other.children and self.parents == other.parents

	def __repr__(self):
		return str(self.list)

	def add(self, node1, node2, label):
		if (node1,label,node2) not in self.list:
			self.list.append((node1,label,node2))

		if (node2,label) not in self.children[node1]:
			self.children[node1].append((node2,label))
		if (node1,label) not in self.parents[node2]:
			self.parents[node2].append((node1,label))

	def dfs(self, root, visited):
		lst = []
		for (child,label) in self.children[root]:
			lst.append((root.variable(),root.amrconcept(),label,child.variable(),child.amrconcept()))
			if child not in visited:
				visited.append(child)
				lst.extend(self.dfs(child,visited))
		return lst

	def _isConnToRoot(self, node, visited):
		if node in visited:
			return False
		visited.append(node)

		if node.isRoot:
			return True
		for (father,_) in self.parents[node]:
			if self._isConnToRoot(father, visited):
				return True
		return False


	def est_depth(self, node, other = None):
		n = 0
		seen = []
		while node in self.parents and len(self.parents[node]) > 0:
			for i in self.parents[node]:
				node, _ = i
				if node in seen:
					return n
				seen.append(node)
				break
			if node != other:
				n += 1
		return n

	def est_depth_down(self, node, other = None):
		n = 0
		seen = []
		while node in self.children and len(self.children[node]) > 0:
			for i in self.children[node]:
				node, _ = i
				if node in seen:
					return n
				seen.append(node)
				break
			if node != other:
				n += 1
		return n

	def triples(self):
		root = Node(True)
		for node in copy.deepcopy(self.children):
			if node is None:
				continue
			if self._isConnToRoot(node, []) == False and len(self.children[node]) > 0:
				self.add(Node(True), node, ":top")
		lst = self.dfs(root,[])

		if len(self.children[root]) > 1:
			counter = 1
			lst2 = []
			lst2.append(("TOP","",":top","mu","multi-sentence"))
			for v1,c1,l,v2,c2 in lst:
				if v1 == "TOP":
					v1 = "mu"
					c1 = "multi-sentence"
					l = ":snt" + str(counter)
					counter += 1
				lst2.append((v1,c1,l,v2,c2))
			return lst2
		return lst

	def _leftmost(self, node, direction, other = None):
		if node != None:
			if direction == "child":
				lst = self.children[node]
			else:
				lst = self.parents[node]
			if len(lst) > 0:
				candidate = None
				minindex = float("inf")
				for item in lst:
					if item[0].isRoot:
						if item[0] != other:
							return item
					elif item[0].token.index < minindex and item[0] != other:
						candidate = item
						minindex = item[0].token.index
				return candidate
		return None

	def _rightmost(self, node, direction, other = None):
		if node != None:
			if direction == "child":
				lst = self.children[node]
			else:
				lst = self.parents[node]
			if len(lst) > 0:
				candidate = None
				maxindex = -1
				for item in lst:
					if item[0].isRoot and candidate is None and item[0] != other:
						candidate = item
						maxindex = -1
					elif item[0].isRoot == False and item[0].token.index > maxindex and item[0] != other:
						candidate = item
						maxindex = item[0].token.index
				return candidate
		return None

	def leftmost_child(self, node, other = None):
		child = self._leftmost(node, "child", other)
		if child == None:
			return "<NULL>"
		if child[0].isConst:
			return child[0].constant
		elif child[0].isRoot:
			return "<TOP>"
		else:
			return child[0].concept

	def leftmost_grandchild(self, node, other = None):
		child = self._leftmost(node, "child", other)
		if child != None:
			grandchild = self._leftmost(child[0], "child", other)
			if grandchild != None:
				if grandchild[0].isConst:
					return grandchild[0].constant
				elif grandchild[0].isRoot:
					return "<TOP>"
				else:
					return grandchild[0].concept
		return "<NULL>"

	def rightmost_child(self, node, other = None):
		child = self._rightmost(node, "child", other)
		if child == None:
			return "<NULL>"
		if child[0].isConst:
			return child[0].constant
		elif child[0].isRoot:
			return "<TOP>"
		else:
			return child[0].concept

	def rightmost_grandchild(self, node, other = None):
		child = self._rightmost(node, "child", other)
		if child != None:
			grandchild = self._rightmost(child[0], "child", other)
			if grandchild != None:
				if grandchild[0].isConst:
					return grandchild[0].constant
				elif grandchild[0].isRoot:
					return "<TOP>"
				else:
					return grandchild[0].concept
		return "<NULL>"

	def leftmost_parent(self, node, other = None):
		parent = self._leftmost(node, "parent", other)
		if parent == None:
			return "<NULL>"
		if parent[0].isConst:
			return parent[0].constant
		elif parent[0].isRoot:
			return "<TOP>"
		else:
			return parent[0].concept

	def rightmost_parent(self, node, other = None):
		parent = self._rightmost(node, "parent", other)
		if parent == None:
			return "<NULL>"
		if parent[0].isConst:
			return parent[0].constant
		elif parent[0].isRoot:
			return "<TOP>"
		else:
			return parent[0].concept

	def isBasterd(self, node):
		return len(self.parents[node]) == 0

	def children_nodes(self, node):
		return [c[0] for c in self.children[node]]

	def isRel(self, node1, node2, boolean = False):
		assert ((isinstance(node1, Node) or node1 is None) and (isinstance(node2, Node) or node2 is None))

		if node1 is None:
			return None
		if node2 is None:
			return None

		for (node, label) in self.children[node1]:
			if node == node2:
				return label
		return None
