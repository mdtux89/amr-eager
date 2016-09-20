#!/usr/bin/env python
#coding=utf-8

'''
Definition of Action class. An action name can be either 'shiftnew', 'shiftdrop', 'reduce', 'rrel'
or 'lrel'.
If it's a shiftnew, it has 1 arguments: the graphlet that must be shifted, that is the nodes to be
inserted in the stack and the relations between them. If it's a shiftdrop or reduce it has no
arguments. Finally, if it's a relation action, it has two arguments: the index i the stack of the
node it attaches to and the relation label.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''
from resources import Resources
labels = {}
labels_counter = 1
for line in open("resources/relations.txt"):
	labels[line.strip()] = labels_counter
	labels_counter += 1

from node import Node
from graphlet import Graphlet
class Action:
	def __init__(self, name, argv = None):
		assert (name == "shift" or name == "lrel" or name == "lrel2" or name == "rrel" or name == "rrel2" or name == "reduce" or name == "reduce3")
		self.name = name
		self.argv = argv

	def __repr__(self):
		return '<%s %s %s>' % (self.__class__.__name__, self.name, self.argv)

	def __eq__(self, other):
		return self.name == other.name and self.argv == other.argv

	def get_id(self):
		act_id = 0
		if self.name == "shift":
			act_id = 1
		elif self.name == "reduce":
			act_id = 2
		elif self.name == "lrel":
			act_id = 3
		elif self.name == "rrel":
			act_id = 4
		return act_id
