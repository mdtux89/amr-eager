#!/usr/bin/env python
#coding=utf-8

'''
Definition of Variables class. It is used when the oracle is not available
and provides method to decide the next variable name and predict the concept 
label that should be associated with it.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

class Variables():
	def __init__(self):
		self.nvars = 0
		self.existingvars = []

	def nextVar(self):
		while True:
			self.nvars += 1
			v = "v" + str(self.nvars)
			if v not in self.existingvars:
				break
		self.existingvars.append(v)
		return v