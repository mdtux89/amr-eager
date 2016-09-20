from amrdata import *
import sys
from collections import defaultdict

def isPath(i, j, children, visited):
	for c in children[i]:
		if c not in visited:
			visited.append(c)
			if c == j:
				return True
			else:
				if isPath(c, j, children, visited):
					return True
	return False

prefix = sys.argv[1]
sents = AMRDataset(prefix, True, False).getAllSents()

narcs = 0
nonp_arc = 0
nonp = 0
nsents = len(sents)

reentrancies = 0
reentr_sent = 0
id_s = 1
for s in sents:
	al_inv = {}
	al = {}
	for key in s.alignments:
		for v in s.alignments[key]:
				if v not in al_inv or al_inv[v] > key:
					al_inv[v] = key
					al[key] = v

	# print s.tokens
	children = defaultdict(list)
	parents = defaultdict(list)
	for a in s.relations:
		children[a[0]].append(a[2])
		parents[a[2]].append(a[0])

	reentr = False
	for item in parents:
		if len(parents[item]) > 1 and item in [str(k) for k in s.amr_api.var2concept().keys()]:
			# for p in parents[item]:
			# 	if len(set(parents[p]).intersection(parents[item])) > 0:
			# 		print "sibling"
			# 	else:
			# 		print "unrelated"

			ch = al_inv[item]
			par = [al_inv[k] for k in parents[item]]
			# print ch
			# print par
			par.sort()
			patt = ""
			for p in par:
				if p < ch:
					patt += "right"
				elif p > ch:
					patt += "left"
				else:
					patt += "?"
			#if patt == "rightleft":
			#	print "# ::id " + str(id_s)
			#	id_s += 1
			#	print "# ::snt " + " ".join(s.tokens)
			#	print s.graph
			#	print ""
			reentr = True
		reentrancies += len(parents[item]) - 1
	if reentr:
		reentr_sent += 1
	# raw_input()

	###############################################

	arcs = []
	for r in s.relations:
		if r[0] == "TOP" or r[0] not in al_inv or r[2] not in al_inv:
		        continue
		arcs.append((al_inv[r[0]],al_inv[r[2]]))

	children = defaultdict(list)
	parents = defaultdict(list)
	for a in arcs:
		if a[1] not in children[a[0]] and a[0] != a[1]:
			children[a[0]].append(a[1])
			parents[a[1]].append(a[0])

	proj = True
	for a in arcs:
		narcs += 1
		head = a[0]
		dep = a[1]
		i = min(head, dep)
		j = max(head, dep)
		for index in range(i + 1, j):
			if index in al:
				if isPath(head, index, children, []) == False:
					nonp_arc += 1
					proj = False
					break

	if proj == False:
		nonp +=1

print "Percentage of non projective sentences:", int(round(nonp / float(nsents)*100))
print "Percentage of non projective arcs:", int(round(nonp_arc / float(narcs)*100))

print "Percentage of sentences with at least a reentrancy:", int(round(reentr_sent / float(nsents)*100))
print "Percentage of reentrant arcs:", int(round(reentrancies / float(narcs)*100))
