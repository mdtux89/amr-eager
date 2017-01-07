#!/usr/bin/env python
#coding=utf-8

'''
Definition of Buffer class. It represents the buffer of the transition system as a
list of 'BufToken'. Only the first item in the list can be removed.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

import embs

class Buffer:
    def __init__(self, embs, tokens, alignments):
        self.embs = embs
        self.tokens = tokens
        if alignments is not None:
            for token, al in zip(tokens, alignments):
                token.nodes = al

    def __repr__(self):
        buf = [item.word for item in self.tokens]
        return '<%s %s>' % (
            self.__class__.__name__, buf)

    def size(self):
        return len(self.tokens)

    def reorder(self, deps, N):
        order = deps.postorder(N)
        if order is not None:
            self.tokens = order

    def isEmpty(self):
        return self.tokens == []

    def consume(self):
        return self.tokens.pop(0)

    def peek(self, index = 0):
        if len(self.tokens) > index:
            return self.tokens[index]
        return None

    def next(self):
        return self.tokens[1]

    def words(self, K, start = 0):
        ret = []
        for item in self.tokens[start:(K+start)]:
            ret.append(self.embs.words.get(item.word))
        for i in range(len(ret), K):
            ret.append(self.embs.words.get("<NULL>"))
        assert(len(ret) == K)
        return ret

    def pos(self, K, start = 0):
        ret = []
        for item in self.tokens[start:(K+start)]:
            ret.append(self.embs.pos.get(item.pos))
        for i in range(len(self.tokens), K):
            ret.append(self.embs.pos.get("<NULLPOS>"))
        assert(len(ret) == K)
        return ret

    def nes(self, K, start = 0):
        ret = []
        for item in self.tokens[start:(K+start)]:
            ret.extend(self.embs.nes.get(item.ne))
        for i in range(len(self.tokens), K):
            ret.extend(self.embs.nes.get("<NULLNE>"))
        return ret

    def  __eq__(self, other):
        return other is not None and self.tokens == other.tokens
        
