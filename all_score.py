import sys
import src.amr
import re
pred = open(sys.argv[1]).read().split("\n\n")
gold = open(sys.argv[2]).read().split("\n\n")

inters = 0
golds = 0
preds = 0
for amr_pred, amr_gold in zip(pred, gold):
        while amr_pred.startswith("#"):
                amr_pred = re.sub("^#.*\n","",amr_pred)
        while amr_gold.startswith("#"):
                amr_gold = re.sub("^#.*\n","",amr_gold)
	amr1 = src.amr.AMR(amr_pred)
	dict1 = amr1.var2concept()
	amr2 = src.amr.AMR(amr_gold)
	dict2 = amr2.var2concept()

	list_pred = []
	for t in amr1.triples(normalize_inverses=True):
		if t[0] not in dict1:
			dict1[t[0]] = t[0] 
		if t[2] not in dict1:
			dict1[t[2]] = t[2]
		list_pred.append((dict1[t[0]],t[1],dict1[t[2]]))

	list_gold = []
	for t in amr2.triples(normalize_inverses=True):
		if t[0] not in dict2:
			dict2[t[0]] = t[0]
		if t[2] not in dict2:
			dict2[t[2]] = t[2]
		list_gold.append((dict2[t[0]],t[1],dict2[t[2]]))

	inters += len(list(set(list_pred) & set(list_gold)))
	preds += len(set(list_pred))
	golds += len(set(list_gold))

if preds > 0:
	pr = inters/float(preds)
else:
	pr = 0
if golds > 0:
	rc = inters/float(golds)
else:
	rc = 0
if pr + rc > 0:
	f = 2*(pr*rc)/(pr+rc)
	print '%.2f' % float(f)

else: 
	print "0.00"

