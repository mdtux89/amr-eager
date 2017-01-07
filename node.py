#!/usr/bin/env python
#coding=utf-8

'''
Definition of Node class. It represents an AMR node in the stack of the transition system.
The variable name and the concept label must have been determined from the token that 
generated it (aligned to it).

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

class Node:
    def __init__(self, token, var = None, concept = None, isConst = None):
        assert (type(token) == bool and token == True) or (var is not None and isConst is not None)
        if type(token) == bool and token == True: # special case for top node, use token as boolean flag
            self.isRoot = True
            self.token = None
            self.isConst = None
            self.constant = None
            self.concept = None
            self.var = None
        else:
            self.isRoot = False
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

    def __ne__(self, other):
        return not(self == other)

    def __hash__(self):
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
            return self.concept
