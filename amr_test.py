#!/usr/bin/env python
#coding=utf-8

'''
@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 02-06-16
'''

from amrdata import *

data = AMRDataset("test.txt")

amr = data.getSent(0)

print amr.tokens
print amr.lemmas
print amr.pos
print amr.nes

print amr.graph
print amr.variables
print amr.relations

print amr.dependencies

print amr.alignments

print amr.amr_api.contains_cycle()
