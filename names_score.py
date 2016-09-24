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
	#print amr_pred
	amr1 = src.amr.AMR(amr_pred)
	amr2 = src.amr.AMR(amr_gold)
	list_pred = []
	list_gold = []
	names = [t[0] for t in amr1.triples(dep=src.amr.Concept("name"))]
	for n in names:
		list_pred.append("_".join([str(v2) for (v1,l,v2) in amr1.role_triples(head=n) if l.startswith(":op")]))

	names =  [t[0] for t in amr2.triples(dep=src.amr.Concept("name"))]
        for n in names:
                list_gold.append("_".join([str(v2) for (v1,l,v2) in amr2.role_triples(head=n) if l.startswith(":op")]))	
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



# amrs_pred = open(sys.argv[1]).read().split("#::")
# amrs_gold = open(sys.argv[2]).read().split("#::")

# print len(amrs_pred), len(amrs_gold)

# for amr_pred, amr_gold in zip(amrs_pred, amrs_gold):
# 	# print amr_pred
# 	# print amrs_gold
# 	raw_input()
# 	list_pred = amr_pred.split("\n")
# 	list_gold = amr_gold.split("\n")

# 	inters = len(list(set(list_pred) & set(list_gold)))
# 	pr = inters/len(list_pred)
# 	rc = inters/len(list_gold)
# 	f = 2*(pr*rc)/(pr+rc)
# 	print pr, rc, f
