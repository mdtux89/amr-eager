#!/usr/bin/env python2.7
#coding=utf-8
'''

@author: Nathan Schneider (nschneid@inf.ed.ac.uk)
@since: 2015-05-06
'''
from __future__ import print_function
import sys, re, fileinput, codecs
from collections import Counter, defaultdict

from amr import AMR, AMRSyntaxError, AMRError, Concept, AMRConstant

c = Counter()
for ln in fileinput.input():
    try:
        a = AMR(ln)
        c.update(map(repr, a.nodes.keys()))    # vars, concepts, constants: count once per AMR
        c.update('.'+repr(x) for _,r,x in a.triples(rel=':instance-of'))  # concepts count once per variable
        c.update(map((lambda x: x[1]), a.triples()))    # relations
        c.update('.'+repr(x) for _,_,x in a.triples() if isinstance(x,AMRConstant))  # constants count once per relation
    except AMRSyntaxError as ex:
        print(ex, file=sys.stderr)
    except AMRError as ex:
        print(ex, file=sys.stderr)
    
for k,n in c.most_common():
    print(k,n, sep='\t')
