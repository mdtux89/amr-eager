#!/usr/bin/env python
#coding=utf-8

'''
Definition of Subgraph class. It contains the nodes and relations of an AMR
subgraph used during concept identification (the term is misleading: both concepts
and relationship between them are retrieved).

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 3-10-16
'''

import copy
from variables import Variables
class Subgraph:

    def __init__(self, nodes, relations):
        self.nodes = nodes
        self.relations = relations

    def get(self, token = None, variables = None):
        if variables == None:
            return self

        tr = {}
        nodes = copy.deepcopy(self.nodes)
        relations = copy.deepcopy(self.relations)
        vs = []
        for (n1,n2,_) in relations:
            vs.append(n1)
            vs.append(n2)
        for n in nodes:
            vs.append(n)
        for n in vs:
            if n.var is not None and n.var not in tr:
                v = variables.nextVar()
                tr[n.var] = v

        seen = []
        for (n1,n2,_) in relations:
            n1.token = token
            n2.token = token
            if n1.var is not None and n1 not in seen:
                n1.var = tr[n1.var]
                seen.append(n1)
            if n2.var is not None and n2 not in seen:
                n2.var = tr[n2.var]
                seen.append(n2)
        for n in nodes:
            n.token = token
            if n.var is not None and n not in seen:
                n.var = tr[n.var]
                seen.append(n)

        return Subgraph(nodes, relations)

    def __eq__(self, other):
        self2 = self.get(None,Variables())
        other2 = other.get(None,Variables())

        return self2.nodes == other2.nodes and self2.relations == other2.relations

    def __ne__(self, other):
        return self.__eq__(other) == False

    def __hash__(self):    
        self2 = self.get(None,Variables())
        return hash((tuple(self2.nodes), tuple(self2.relations)))

    def __repr__(self):
        return '<%s %s %s>' % (
            self.__class__.__name__, self.nodes, self.relations)

