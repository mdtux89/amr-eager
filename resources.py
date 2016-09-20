from collections import defaultdict
import cPickle as pickle
from scipy.sparse import lil_matrix
import operator
from graphlet import Graphlet
from node import Node
from variables import Variables

class Resources:
	phrasetable = None

	@staticmethod
	def store_table():

		table = {}
		freq = {}
		print "Storing tables.."
		print "Number of tokens:", len(Resources.phrasetable.keys())
		shifts = set()
		for i, token in enumerate(Resources.phrasetable):
			#for item in Resources.phrasetable[token]:
			#	if Resources.phrasetable[token][item] > 5:
			#		shifts.add(item)

			if i % 100 == 0:
				print "Token:", i

			gl = max(Resources.phrasetable[token].iteritems(), key=operator.itemgetter(1))[0]
			f = 0
			for item in Resources.phrasetable[token].iteritems():
				f += item[1]
			freq[token] = f
			table[token] = gl

		pickle.dump(table, open("resources/phrasetable.p", "wb"))
		#pickle.dump(sorted(shifts), open("resources/shifts.p", "wb"))

		pickle.dump(freq, open("resources/tokfreqs.p", "wb"))
		pickle.dump(Resources.list_gl, open("resources/graphlets.p", "wb"))

	@staticmethod
	def init_table(empty = True):
		Resources.phrasetable = defaultdict(lambda : defaultdict(int))

		if empty == False:
			Resources.phrasetable = pickle.load(open("resources/phrasetable.p", "rb"))
			Resources.tokfreqs = pickle.load(open("resources/tokfreqs.p", "rb"))
			Resources.graphlets = pickle.load(open("resources/graphlets.p", "rb"))
		else:
			Resources.seen_ne = []
			Resources.list_gl = []
			Resources.seen_gl = defaultdict(int)
			Resources.fne = open("resources/namedentities.txt","w")
			Resources.forg = open("resources/organizations.txt","w")
			Resources.fgl = open("resources/graphlets.txt","w")

		Resources.verbalization_list = {}
		for line in open("resources/verbalization-list-v1.06.txt"):
			line = line.strip().split()
			if line[0] == "VERBALIZE":
				var = Variables()
				nodes = []
				ntop = Node(None, var.nextVar(), line[3], False)
				nodes.append(ntop)
				relations = []
				fields = line[4:]
				for i in range(0,len(fields),2):
					if fields[i + 1] == "-":
						n = Node(None, '-', "", True)
					else:
						n = Node(None, var.nextVar(), fields[i + 1], False)
					nodes.append(n)
					relations.append((ntop,n,fields[i]))
				Resources.verbalization_list[line[1]] = Graphlet(nodes, relations)
		for line in open("resources/have-org-role-91-roles-v1.06.txt"):
			line = line.strip().split()
			if line[0] == "USE-HAVE-ORG-ROLE-91-ARG2":
				var = Variables()
				ntop = Node(None, var.nextVar(), "have-org-role-91", False)
				node = Node(None, var.nextVar(), line[1], False)
				Resources.verbalization_list[line[1]] = Graphlet([ntop, node], [(ntop, node, ":ARG2")])

		for line in open("resources/have-rel-role-91-roles-v1.06.txt"):
			if "#" in line:
				line = line.split("#")[0]
			line = line.strip().split()
			if len(line) > 0 and line[0] == "USE-HAVE-REL-ROLE-91-ARG2":
				var = Variables()
				if len(line) >= 3 and line[2] == ":standard":
					ntop = Node(None, var.nextVar(), "have-rel-role-91", False)
					node = Node(None, var.nextVar(), line[3], False)
					Resources.verbalization_list[line[1]] = Graphlet([ntop, node], [(ntop, node, ":ARG2")])
					Resources.verbalization_list[line[3]] = Graphlet([ntop, node], [(ntop, node, ":ARG2")])
				else:
					ntop = Node(None, var.nextVar(), "have-rel-role-91", False)
					node = Node(None, var.nextVar(), line[1], False)
					Resources.verbalization_list[line[1]] = Graphlet([ntop, node], [(ntop, node, ":ARG2")])
