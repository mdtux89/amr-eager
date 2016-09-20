#!/usr/bin/env python
#coding=utf-8

'''
Definition of routine to get the most likely label for each word.

@author: Marco Damonte (s1333293@inf.ed.ac.uk)
@since: 23-02-13
'''

from collections import defaultdict
import operator

def get_w2c_dict():
	w2c_list = {}
	for line in open("resources/w2c.txt"):
		t = line.split()
		if len(t) != 2:
			continue

		if t[0] not in w2c_list:
			w2c_list[t[0]] = defaultdict(int)

		w2c_list[t[0]][t[1]] += 1

	w2c = {}
	for k in w2c_list:
		sorted_x = sorted(w2c_list[k].items(), key=operator.itemgetter(1))
		w2c[k] = sorted_x[-1][0]

	return w2c