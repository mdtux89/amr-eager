import smatch.amr as amr
import sys
import re
from amrdata import *
from collections import defaultdict
import copy
def _to_string(triples, root, level, last_child, seen, prefix, indexes):
    children = [t for t in triples if str(t[0]) == root.split()[0]]
    if root in seen:
        root = root.split()[0]
        children = []
    else:
        var = root
        if " / " in root:
            var = root.split()[0]
        indexes[var].append(prefix)
    if " / " in root:
        seen.append(root)
        graph = "(" + root
        if len(children) > 0:
            graph += "\n"
        else:
            graph += ")"
    else:
        graph = root
    j = 0
    for k, t in enumerate(children):
        if str(t[0]) == root.split()[0]:
            next_r = t[3]
            if t[4] != "":
                next_r += " / " + t[4]
            for i in range(0, level):
                graph += "    "
            seen2 = copy.deepcopy(seen)
            graph += t[2] + " " + _to_string(triples, next_r, level + 1, k == len(children) - 1, seen, prefix + "." + str(j), indexes)[0]
            if next_r not in seen2 or " / " not in next_r:
                j += 1
    if len(children) > 0:
        graph += ")"
    if not last_child:
        graph += "\n"

    return graph, indexes

def to_string(triples, root):
 #   print triples
    children = [t for t in triples if str(t[0]) == root]
#    print root
#    print "--"
#    print ""
    if len(children) > 1:
    	counter = 1
        triples2 = [("TOP","",":top","mu","multi-sentence")]
        for t in triples:
            if t[0] == "TOP":
                triples2.append(("mu", "multi-sentence", ":snt" + str(counter), t[3], t[4]))
                counter += 1
            else:
                triples2.append(t)
    else:
        triples2 = triples
    children = [t for t in triples2 if str(t[0]) == root]
    assert(len(children) == 1)
    if children[0][4] == "":
        return "(e / emptygraph)\n", defaultdict(list)
    return _to_string(triples2, children[0][3] + " / " + children[0][4], 1, False, [], "0", defaultdict(list))

def var2concept(amr):
        v2c = {}
        for n, v in zip(amr.nodes, amr.node_values):
                v2c[n] = v
        return v2c

prefix = sys.argv[1]
blocks = open(prefix + ".out").read().split("\n\n")
nps = []
npstart = False
par = 0
k = -1
sents = AMRDataset(prefix, True, False).getAllSents()
famr = open("np_graphs.txt","w")
fsent = open("np_sents.txt","w")
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
		if const[i] == "(" and const[i + 1] == "N" and const[i + 2] == "P" and const[i + 3] == " ":
		#if npstart == False and const[i] == "(" and const[i + 1] == "N" and const[i + 2] == "P" and const[i + 3] == " ":
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
		if nodes == []: # no alignments
			continue
		v2c = defaultdict(str)
		amr_annot = amr.AMR.parse_AMR_line(sents[k].graph.replace("\n",""))
		for key in var2concept(amr_annot):
			v2c[str(key)] = str(var2concept(amr_annot)[key])
		rels = [r for r in sents[k].relations if r[0] in nodes and r[2] in nodes]
#		for node in nodes:
#			if node not in [r[0] for r in rels] and node not in [r[2] for r in rels]:
#				rels.insert(0, ("TOP", ":top", node))
		
		rels2 = [(r[0], v2c[r[0]], r[1], r[2], v2c[r[2]]) for r in rels]
		if len(rels2) > 0:
			rels2.insert(0, ("TOP", "", ":top", rels2[0][0], v2c[rels2[0][0]]))
			
		for node in nodes:
			if node not in [r[0] for r in rels2] and node not in [r[3] for r in rels2]:
				rels2.insert(0, ("TOP", "", ":top", node, v2c[node]))
		famr.write(to_string(rels2, rels2[0][0])[0] + "\n")
		fsent.write(" ".join(n) + "\n")
		#rels2 = MyRelations(rels2).triples()
		
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

		#if rels2 != [] and str(src.amr.AMR.triples2String(rels2)).startswith("("):
		#	print "# ::snt", " ".join(n)
		#	graph = src.amr.AMR.triples2String(rels2)
		#	print graph
		#	print ""
