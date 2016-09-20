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

class DropArcs:
	def __init__(self):
		self.children = {} 

	def add(self, node1, node2, label):
		if node1 not in self.children:
			self.children[node1] = {}
		if node2 not in self.children[node1]:
			self.children[node1][node2] = []	

		self.children[node1][node2].append(label)

	def kth_label(self, node1, node2, k):
		if node1 not in self.children or node2 not in self.children[node1]:
			return "<NULL>" 
		a = self.children[node1][node2][::-1]
		return a[k]
