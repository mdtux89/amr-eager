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
	amr2 = src.amr.AMR(amr_gold)
	v2c1 = amr1.var2concept()
	v2c2 = amr2.var2concept()
	list_pred = []
	vrs = []
	for t in amr1.role_triples():
		if t[1].startswith(":ARG"):
			list_pred.append(t)
			vrs.extend([t[0],t[2]])
        dict1 = {}
        d = amr1.var2concept()
        for i in d:
                 if i in vrs:
                        dict1[i] = d[i]

        list_gold = []
        for t in amr2.role_triples(): 
                if t[1].startswith(":ARG"):
                        list_gold.append(t)
			vrs.extend([t[0],t[2]])
        dict2 = {}
        d = amr2.var2concept()
        for i in d:
                 if i in vrs:
                        dict2[i] = d[i]

        allamrs1.append((list_pred,dict1))
        allamrs2.append((list_gold,dict2))

pickle.dump(allamrs1, open("amrs1.p", "wb"))
pickle.dump(allamrs2, open("amrs2.p", "wb"))
output = subprocess.check_output(['python','../smatch_2.0.2/smatch_edited.py', '--pr', '-f', "amrs1.p", "amrs2.p"])
print output.strip()
subprocess.check_output(["rm", "amrs1.p"])
subprocess.check_output(["rm", "amrs2.p"])
