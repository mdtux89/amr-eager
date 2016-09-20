#!/usr/bin/env python
#coding=utf-8

'''
Definition of Node class. It represents an AMR node in the stack of the transition system.
The variable name and the concept label must have been determined from the token that 
generated it (aligned to it).

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

class Node:
	def __init__(self, token, var = None, concept = None, isConst = None):
		assert (type(token) == bool and token == True) or (var != None and isConst != None)
		if type(token) == bool and token == True: # special case for top node, use token as boolean flag
			self.isRoot = True
			self.isBasterd = False
			# self.reducedchild = None
			self.token = None
			self.isConst = None
			self.constant = None
			self.concept = None
			self.var = None
		else:
			# self.reducedchild = None
			self.isRoot = False
			self.isBasterd = True
			self.token = token
			if isConst:
				self.isConst = True
				self.constant = var
				self.var = None
			else:
				self.isConst = False
				self.var = var
				self.constant = None

			if concept == None:
				self.concept = None
			else:
				self.concept = concept.encode('utf-8').strip()
	def __eq__(self, other):
		return str(self) == str(other)
		# return self.__hash__() == other.__hash__()

	def __ne__(self, other):
		return not(self == other)

	def __hash__(self):
		# return hash((self.isRoot, self.isConst, self.concept, self.var, self.constant))
		return hash((self.__repr__()))

	def __repr__(self):
		if self.isRoot:
			return '<%s %s>' % (
     		self.__class__.__name__, "TOP")	
		else:
			if self.isConst:
				return '<%s %s %s %s>' % (
     				self.__class__.__name__, "const", self.constant, self.concept)
			else:
				return '<%s %s %s>' % (
     				self.__class__.__name__, self.var, self.concept)
				
	def variable(self):
		if self.isRoot:
			return "TOP"
		elif self.isConst:
			return self.constant
		else:
			return self.var

	def amrconcept(self):
		if self.isRoot:
			return ""
		elif self.isConst:
			return ""
		else:
			# if self.concept[0] == '"':
			# 	self.concept = self.concept[1:]
			# if self.concept[-1] == '"':
			# 	self.concept = self.concept[:-1]
			return self.concept
