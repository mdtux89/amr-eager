#!/usr/bin/env python
#coding=utf-8

'''
Definition of Dependencies class. It store all dependency arcs of the sentence and provides
methods to check if two tokens are connected by an arc and to extract all incoming and outgoing
edges of a token.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

from collections import defaultdict
from buftoken import BufToken

class Dependencies:
	def __init__(self, deps):
		self.children = defaultdict(set)
		self.parents = defaultdict(set)

		for (n1, label, n2) in deps:
			assert (isinstance(n1, BufToken) and isinstance(n2, BufToken) and type(label) == str)
			self.add(n1, n2, label)

	def add(self, node1, node2, label):
		assert (isinstance(node1, BufToken) and isinstance(node2, BufToken) and type(label) == str)
		self.children[node1].add((node2,label))
		self.parents[node2].add((node1,label))

	def isArc(self, node1, node2, seen):
		assert (isinstance(node1, BufToken) and isinstance(node2, BufToken))
		
		#if node1 is None:
		#	node1 = node2
		#elif node2 is None:
		#	return "<NULLDEP>"

		# seen.append(node1)
		# for (node, label) in self.children[node1]:
		# 	if node == node2:
		# 		return label
		# 	if node not in seen:
		# 		label = self.isArc(node, node2, seen)
		# 		if label != "<NULLDEP>":
		# 			return label

		for (node, label) in self.children[node1]:
			if node == node2:
				return label
				
		return "<NULLDEP>"

	def lm_grandparent(self, node1):
		minind = float("inf")
		p = None
                for node, _ in self.parents[node1]:
			print node, minind, node1
			if node.index < minind:# and node != node1:
				minind = node.index
				p = node
		if p is None:
			return 0
			#return "<NULLDEP>"
		minind = float("inf")
		cand = None
		for n,l in self.parents[p]:
			if n.index < minind:# and n != p:
				minind = n.index
				cand = l
		if cand is None:
			return 0
			#return "<NULLDEP>"
		else:
			return 1
			#return cand
	def isGrandArc(self, node1, node2, seen):
	       	seen.append(node1)
                for (node, label) in self.children[node1]:
                        if node not in seen:
                                label = self.isArc(node, node2, seen)
                                if label != "<NULLDEP>":
					return label
		return "<NULLDEP>"


	# def distance(self, node1, node2, seen, distance):
	# 	assert ((isinstance(node1, BufToken) or node1 is None) and (isinstance(node2, BufToken) or node2 is None))

	# 	if node1 is None:
	# 		node1 = node2
	# 	elif node2 is None:
	# 		return 0

	# 	seen.append(node1)
	# 	for (node, label) in self.children[node1]:
	# 		if node == node2:
	# 			return distance
	# 		if node not in seen:
	# 			distance = self.distance(node, node2, seen, distance + 1)
	# 			if label != "<NULLDEP>":
	# 				return distance
					
	# 	# for (node, label) in self.children[node1]:
	# 	# 	if node == node2:
	# 	# 		return label
				
	# 	return 0

	def nArcs(self, node1, node2):
		assert ((isinstance(node1, BufToken) or node1 is None) and (isinstance(node2, BufToken) or node2 is None))

		counter = 0
		for (node, label) in self.children[node1]:
			if node == node2:
				counter += 1
		return counter

	def areSiblings(self, node1, node2):
		assert ((isinstance(node1, BufToken) or node1 is None) and (isinstance(node2, BufToken) or node2 is None))
		if len(self.parents[node1]) == 0 or len(self.parents[node2]) == 0:
			return 0

		for item1 in self.parents[node1]:
			if item1[1] == "ROOT":
				continue 
			p1 = item1[0]
			for item2 in self.parents[node2]:
				if item2[1] == "ROOT":
					continue 
				p2 = item2[0]
				if p1 == p2:
					return 1
		return 0

	def areAdjacients(self, node1, node2):
		assert ((isinstance(node1, BufToken) or node1 is None) and (isinstance(node2, BufToken) or node2 is None))
		if len(self.parents[node1]) == 0 or len(self.parents[node2]) == 0:
			return 0
		
		for item1 in self.parents[node1]:
			if item1[1] == "ROOT":
				continue 
			p1 = item1[0]
			for item2 in self.parents[node2]:
				if item2[1] == "ROOT":
					continue
				p2 = item2[0]

				if p1 == p2:
					flag = False
					for c, _ in self.children[p1]:
						if node1.index < node2.index:
							a = node1.index
							b = node2.index
						else:
							a = node2.index
							b = node1.index
						if c.index > a and c.index < b:
							flag = True
							break
					if flag == False:
						return 1
		return 0

	def n_outgoing(self, node, isroot, candidates):
		assert (isinstance(node, BufToken) or node is None)
		# if isroot: ### commenting because doesnt seem to help
		# 	for n in candidates:
		# 		for (p,label) in self.parents[n]:
		# 			if label == "ROOT":
		# 				return 1
		# 	return 0
		return len([(c,l) for (c,l) in self.children[node] if c in candidates])


	def n_incoming(self, node, isroot, candidates):
		assert (isinstance(node, BufToken) or node is None)
		if isroot:
			return 0
		return len([(c,l) for (c,l) in self.parents[node] if c in candidates])

	def _postorder(self, root, visited, N):
		# print root
		# raw_input()
		lst = []
		visited.append(root)
		lst.append(root)
		# left = [c for c in self.children[root] if c[0].index < root.index]
		# right = [c for c in self.children[root] if c[0].index > root.index]
		for i in range(0, N):
			for (child,label) in self.children[root]:
				if child != root and child not in visited:
					diff = abs(child.index - root.index)
					if diff == i:
						lst.extend(self._postorder(child, visited, N))
		# for i in range(0,len(self.children.keys())):
		# 	for (child,label) in right:
		# 		if child != root and child not in visited:
		# 			diff = abs(child.index - root.index)
		# 			if diff == i:
		# 				lst.extend(self._postorder(child, visited))
		return lst
		# for (child,label) in self.children[root]:
		# 	if child != root:
		# 		if child not in visited:
		# 			lst.extend(self._postorder(child, visited))
		# return lst
		
	def postorder(self, N):
		roots = []

		for node in self.children:
			for (child, label) in self.children[node]:
				if label == "ROOT":
					roots.append(node)
		assert (roots != [])
		assert (len(roots) == 1) # if this not true, which root should I choose to syntactically realize the stack's root?

		order = []
		for root in roots:
			order.extend(self._postorder(root, [], N))
		if order == []:
			return None
		return order
		
	def minundirpath(self, node1, node2):
		if node1 is None:
			node1 = node2
		if node2 is None:
			node2 = node1

		assert(node1 in self.children or node1 in self.parents)
		assert(node2 in self.children or node2 in self.parents)

		queue = [node1]
		seen = []
		bp = {}
		while len(queue) > 0:
			item = queue.pop(0)
			seen.append(item)
			if item == node2:
				ret = []
				while item in bp:
					#ret.append((item.word,item.pos))
					#ret.append(bp[item][1]+"_DEP")
					ret.append(bp[item][1])
					item = bp[item][0]
				#ret.append(item.word)
				#ret.append((item.word,item.pos))
				if ret == []:
					ret = ["ROOT"]
				else:
					ret.reverse()
				return ret
			for (child, label) in self.children[item]:
				if child not in seen:
					queue.append(child)
					bp[child] = (item,label)
			for (parent, label) in self.parents[item]:
				if parent not in seen:
					queue.append(parent)
					bp[parent] = (item,label)
		return None
