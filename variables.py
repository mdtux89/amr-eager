#!/usr/bin/env python
#coding=utf-8

'''
Definition of Variables class. It is a provider of variable names to avoid
conflicting variables.  

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
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
