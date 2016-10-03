import sys
import src.amr
import re
import cPickle as pickle
import subprocess

pred = open(sys.argv[1]).read().split("\n\n")
gold = open(sys.argv[2]).read().split("\n\n")

allamrs1 = []
allamrs2 = []
for amr_pred, amr_gold in zip(pred, gold):
        while amr_pred.startswith("#"):
                amr_pred = re.sub("^#.*\n","",amr_pred)
        while amr_gold.startswith("#"):
                amr_gold = re.sub("^#.*\n","",amr_gold)

	amr1 = src.amr.AMR(amr_pred)
        list_pred = []
	vrs = []
        for n in amr1.reentrancies().items():
                for t in amr1.triples(dep=n[0]):
                        list_pred.append(t)
			vrs.extend([t[0],t[2]])
	dict1 = {}
	d = amr1.var2concept()
	for i in d:
		 if i in vrs:
			dict1[i] = d[i]
	amr2 = src.amr.AMR(amr_gold)
	list_gold = []
	vrs = []
        for n in amr2.reentrancies().items():
                for t in amr2.triples(dep=n[0]):
                        list_gold.append(t)
			vrs.extend([t[0],t[2]])
        dict2 = {}
        d = amr2.var2concept()
        for i in d:
                 if i in vrs:
                        dict2[i] = d[i]

	#print list_pred
	#print list_gold
	#print dict1
	#print dict2
	#raw_input()

	allamrs1.append((list_pred,dict1))
	allamrs2.append((list_gold,dict2))

pickle.dump(allamrs1, open("amrs1.p", "wb"))
pickle.dump(allamrs2, open("amrs2.p", "wb"))
output = subprocess.check_output(['python','../smatch_2.0.2/smatch_edited.py', '--pr', '-f', "amrs1.p", "amrs2.p"])
print output.strip()
subprocess.check_output(["rm", "amrs1.p"])
subprocess.check_output(["rm", "amrs2.p"])
	
#	inters += len(list(set(list_pred) & set(list_gold)))
#	preds += len(set(list_pred))
#	golds += len(set(list_gold))
#
#if preds > 0:
#	pr = inters/float(preds)
#else:
#	pr = 0
#if golds > 0:
#	rc = inters/float(golds)
#else:
#	rc = 0
#if pr + rc > 0:
#	print pr, rc
#	f = 2*(pr*rc)/(pr+rc)
#	print '%.2f' % float(f)
#
#else: 
#	print "0.00"
#
