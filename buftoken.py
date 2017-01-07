#!/usr/bin/env python
#coding=utf-8

'''
Definition of BufToken class. It represents a token in the buffer of the transition system.
MWEs are stored in a single token (taken care during preprocessing). 'nodes' is the list of
objects of class Nodes that this token is aligned to; it contains 'None' if alignments are not
available (parsing mode, no oracle).

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

class BufToken:

    def __init__(self, word, lemma, ne, pos, index, nodes):
        self.word = word
        self.lemma = lemma
        self.ne = ne
        self.pos = pos
        self.index = index
        self.nodes = nodes

    def __eq__(self, other):
        return other is not None and self.word == other.word and self.lemma == other.lemma and self.pos == other.pos and self.ne == other.ne and self.index == other.index 

    def __repr__(self):
        return '<%s %s %s %s %s %s %s>' % (
            self.__class__.__name__, str(self.word), str(self.lemma), self.ne, self.pos, self.index, self.nodes)

    def __hash__(self):
        return hash((self.word, self.lemma, self.ne, self.pos, self.index))
