#!/usr/bin/env python
#coding=utf-8

'''
Definition of Oracle class. Given the gold AMR graph, the alignments and
the current state, it decides which action should be taken next.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

from action import Action
from relations import Relations
import copy
from subgraph import Subgraph

class Oracle:

    def reentrancy(self, node, found):
        siblings = [item[0] for p in found.parents[node] for item in found.children[p[0]] if item[0] != node]
        for s in siblings:
            label = self.gold.isRel(node, s)
            if label is not None:
                self.gold.parents[s].remove((node,label))
                self.gold.children[node].remove((s,label))
                parents = [i[0] for i in found.parents[node]]
                parents = [i[0] for i in found.parents[s] if i[0] in parents]
                return [s, label, siblings]
        return None

    def __init__(self, relations):
        self.gold = Relations(copy.deepcopy(relations))

    def valid_actions(self, state):
        top = state.stack.top()

        for i in range(1, 5):
            other = state.stack.get(i)
            label = self.gold.isRel(top, other)
            
            if label is not None:
                if i == 1:
                    self.gold.children[top].remove((other,label))
                    self.gold.parents[other].remove((top,label))
                    return Action("larc", label)
                else:
                    print top, other, label
                    raw_input()

        label = self.gold.isRel(other, top)
        if label is not None:
            self.gold.parents[top].remove((other,label))
            self.gold.children[other].remove((top,label))
            return Action("rarc", label)

        if state.stack.isEmpty() == False:
            found = False
            for item in state.buffer.tokens:
                for node in item.nodes:
                    if self.gold.isRel(top, node) is not None or self.gold.isRel(node, top) is not None:
                        found = True
            if found == False:
                return Action("reduce", self.reentrancy(top, state.stack.relations))

        if state.buffer.isEmpty() == False:
            token = state.buffer.peek()
            nodes = token.nodes
            relations = []
            flag = False
            for n1 in nodes:
                for n2 in nodes:
                    if n1 != n2:
                        children_n1 = copy.deepcopy(self.gold.children[n1])
                        for (child,label) in children_n1:
                            if child == n2:
                                relations.append((n1,n2,label))
                                self.gold.children[n1].remove((child,label))
                                self.gold.parents[child].remove((n1,label))
                        children_n2 = copy.deepcopy(self.gold.children[n2])
                        for (child,label) in children_n2:
                            if child == n1:
                                relations.append((n2,n1,label))
                                self.gold.children[n2].remove((child,label))
                                self.gold.parents[child].remove((n2,label))

            subgraph = Subgraph(nodes, relations)
            return Action("shift", subgraph)

        return None
