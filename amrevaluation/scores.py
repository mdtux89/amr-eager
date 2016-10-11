#!/usr/bin/env python
#coding=utf-8

'''
Computes AMR scores for concept identification, named entity recognition, wikification,
negation detection, reentrancy detection and SRL.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

import sys
import src.amr
import re
from collections import defaultdict
import cPickle as pickle
import subprocess

def concepts(v2c_dict):
	return [str(v) for v in v2c_dict.values()]

def namedent(amr, v2c_dict):
	return [str(v2c_dict[v1]) for (v1,l,v2) in amr.role_triples() if l == ":name"]

def negations(amr, v2c_dict):
	return [v2c_dict[v1] for (v1,l,v2) in amr.role_triples() if l == ":polarity"]	

def wikification(amr):
	return [v2 for (v1,l,v2) in amr.role_triples() if l == ":wiki"]

def reentrancy(amr, v2c_dict):
	lst = []
	vrs = []
	for n in amr.reentrancies().items():
		for t in amr.triples(dep=n[0]):
			lst.append(t)
			vrs.extend([t[0],t[2]])
	dict1 = {}
	d = amr.var2concept()
	for i in d:
		 if i in vrs:
			dict1[i] = d[i]
	return (lst, dict1)

def srl(amr, v2c_dict):
	lst = []
	vrs = []
	for t in amr.role_triples():
		if t[1].startswith(":ARG"):
			lst.append(t)
			vrs.extend([t[0],t[2]])
	dict1 = {}
	d = amr.var2concept()
	for i in d:
		if i in vrs:
			dict1[i] = d[i]
	return (lst, dict1)

pred = open(sys.argv[1]).read().split("\n\n")
gold = open(sys.argv[2]).read().split("\n\n")

inters = defaultdict(int)
golds = defaultdict(int)
preds = defaultdict(int)
reentrancies_pred = []
reentrancies_gold = []
srl_pred = []
srl_gold = []

for amr_pred, amr_gold in zip(pred, gold):
	amr_pred = src.amr.AMR(amr_pred)
	dict_pred = amr_pred.var2concept()
	amr_gold = src.amr.AMR(amr_gold)
	dict_gold = amr_gold.var2concept()

	list_pred = concepts(dict_pred)
	list_gold = concepts(dict_gold)
	inters["Concepts"] += len(list(set(list_pred) & set(list_gold)))
	preds["Concepts"] += len(set(list_pred))
	golds["Concepts"] += len(set(list_gold))

	list_pred = namedent(amr_pred, dict_pred)
	list_gold = namedent(amr_gold, dict_gold)
	inters["Named Ent."] += len(list(set(list_pred) & set(list_gold)))
	preds["Named Ent."] += len(set(list_pred))
	golds["Named Ent."] += len(set(list_gold))

	list_pred = negations(amr_pred, dict_pred)
	list_gold = negations(amr_gold, dict_gold)
	inters["Negations"] += len(list(set(list_pred) & set(list_gold)))
	preds["Negations"] += len(set(list_pred))
	golds["Negations"] += len(set(list_gold))

	list_pred = wikification(amr_pred)
	list_gold = wikification(amr_gold)
	inters["Wikification"] += len(list(set(list_pred) & set(list_gold)))
	preds["Wikification"] += len(set(list_pred))
	golds["Wikification"] += len(set(list_gold))

	reentrancies_pred.append(reentrancy(amr_pred, dict_pred))
	reentrancies_gold.append(reentrancy(amr_gold, dict_gold))
	srl_pred.append(srl(amr_pred, dict_pred))
	srl_gold.append(srl(amr_gold, dict_gold))

for score in preds:
	print score, "->",
	if preds[score] > 0:
		pr = inters[score]/float(preds[score])
	else:
		pr = 0
	if golds[score] > 0:
		rc = inters[score]/float(golds[score])
	else:
		rc = 0
	if pr + rc > 0:
		f = 2*(pr*rc)/(pr+rc)
		print 'P: %.2f, R: %.2f, F: %.2f' % (float(pr), float(rc), float(f))
	else: 
		print 'P: %.2f, R: %.2f, F: %.2f' % (float(pr), float(rc), float("0.00"))

pickle.dump(reentrancies_pred, open("amrs1.p", "wb"))
pickle.dump(reentrancies_gold, open("amrs2.p", "wb"))
output = subprocess.check_output(['python','smatch_2.0.2/smatch_edited.py', '--pr', '-f', "amrs1.p", "amrs2.p"]).strip().split()
print 'Reentrancies -> P: %.2f, R: %.2f, F: %.2f' % (float(output[1]), float(output[3]), float(output[6][0:-1]))

pickle.dump(srl_pred, open("amrs1.p", "wb"))
pickle.dump(srl_gold, open("amrs2.p", "wb"))
output = subprocess.check_output(['python','smatch_2.0.2/smatch_edited.py', '--pr', '-f', "amrs1.p", "amrs2.p"]).strip().split()
print 'SRL -> P: %.2f, R: %.2f, F: %.2f' % (float(output[1]), float(output[3]), float(output[6][0:-1]))

subprocess.check_output(["rm", "amrs1.p"])
subprocess.check_output(["rm", "amrs2.p"])
