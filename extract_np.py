import sys
import re
from amrdata import *
from collections import defaultdict
from myrelations import *
prefix = sys.argv[1]
blocks = open(prefix + ".out").read().split("\n\n")
#alignments = open(prefix + ".alignments").read().split("\n")
nps = []
npstart = False
par = 0
k = -1
sents = AMRDataset(prefix, True, False).getAllSents()
while True:
	k += 1
        if len(blocks) == 1:
                break
        block_txt = blocks.pop(0).strip()
        block = block_txt.split("\n")
	snt = block[1]
	const = "".join(block[3:])
        if blocks[0].startswith("\n"):
                b = ""
        else:
                b = blocks.pop(0)
	nps = []
	for i in range(0,len(const)):
		if npstart:
			npstr += const[i]
		if npstart == False and const[i] == "(" and const[i + 1] == "N" and const[i + 2] == "P" and const[i + 3] == " ":
			npstart = True
			npstr = ""
			par = 0
		elif const[i] == "(":
			par += 1
		elif const[i] == ")":
			if npstart and par == 0:
				npstart = False
				nps.append([w[:-1] for w in re.findall('[\w:\'\/\-\.\,\@][\w:\'\/\-\.\,\@]*\)', npstr)])
			else:
				par -= 1
	snt = sents[k].tokens
	for n in nps:
		nodes = []
		if n == []:
			continue
		a = snt.index(n[0])
		b = snt.index(n[-1])
		for index in range(a, b + 1):
			nodes.extend(sents[k].alignments[index])
		v2c = defaultdict(str)
		for key in sents[k].amr_api.var2concept():
			v2c[str(key)] = str(sents[k].amr_api.var2concept()[key])
		rels = [r for r in sents[k].relations if r[0] in nodes and r[2] in nodes]
		for node in nodes:
                      if node not in [r[0] for r in rels] and node not in [r[2] for r in rels]:
                              rels.insert(0, ("TOP", ":top", node))
		rels2 = [(r[0], v2c[r[0]], r[1], r[2], v2c[r[2]]) for r in rels]
		rels2 = MyRelations(rels2).triples()
		#rels2 = [(r[0], v2c[r[0]], r[1], r[2], v2c[r[2]]) for r in rels]
		#for n in nodes:
		#	if n not in [r[2] for r in rels]:
		#		for i in range(0, len(rels2)):
		#			if rels2[i][0] == n:
		#				rels2.insert(i, ("TOP", "", ":top", n, v2c[n]))
		#				break
		##for n in nodes:
		##	if n not in [r[0] for r in rels] and n not in [r[2] for r in rels]:
		##		rels2.insert(0, ("TOP", "", ":top", n, v2c[n]))
		##if len([r for r in rels2 if r[0] == "TOP"]) == 0 and len(rels2) > 0:
		##	root = rels2[0][0]
		##	rels2.insert(0, ("TOP", "", ":top", root, v2c[root]))
		#if len([r for r in rels2 if r[0] == "TOP"]) > 1:
                 #       counter = 1
                #        lst2 = []
                 #       lst2.append(("TOP","",":top","mu","multi-sentence"))
                #        for v1,c1,l,v2,c2 in rels2:
                #                if v1 == "TOP":
                #                        v1 = "mu"
                #                        c1 = "multi-sentence"
                #                        l = ":snt" + str(counter)
                #                        counter += 1
                #                lst2.append((v1,c1,l,v2,c2))
               # 	rels2 = lst2
		if rels2 != [] and str(src.amr.AMR.triples2String(rels2)).startswith("("):
			print "# ::snt", " ".join(n)
			graph = src.amr.AMR.triples2String(rels2)
			print graph
			print ""
