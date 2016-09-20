import cPickle as pickle
from transition_system import TransitionSystem
from embs import Embs
from resources import Resources
import copy
import sys
import argparse

def collect(prefix):
	Resources.init_table(True)

	print "Loading data.."
	alltokens = pickle.load(open(prefix + ".tokens.p", "rb"))
	alldependencies = pickle.load(open(prefix + ".dependencies.p", "rb"))
	allalignments = pickle.load(open(prefix + ".alignments.p", "rb"))
	allrelations = pickle.load(open(prefix + ".relations.p", "rb"))

	print "Collecting relation labels.."
	seen_r = set()
	fw = open("resources/relations.txt","w")
	for relations in allrelations:
		for r in relations:
			if r[1] not in seen_r:
				fw.write(r[1] + "\n")
				seen_r.add(r[1])
	fw.close()

	print "Collecting dependency labels.."
	seen_d = set()
	fw = open("resources/dependencies.txt","w")
	for dependencies in alldependencies:
		for d in dependencies:
			if d[1] not in seen_d:
				fw.write(d[1] + "\n")
				seen_d.add(d[1])
	fw.close()

	counter = 0
	embs = Embs()
	for tokens, dependencies, alignments, relations in zip(alltokens, alldependencies, allalignments, allrelations):
		counter += 1
		print "Sentence no: ", counter
		data = (tokens, dependencies, relations, alignments)
		t = TransitionSystem(embs, data, "COLLECT", 0)

	Resources.store_table()
	print "Done"

if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-t", "--train", help="Training file to collect seen dependencies, AMR relations and other info", required = True)

	try:
	    args = argparser.parse_args()
	except:
	    argparser.error("Invalid arguments")
	    sys.exit(0)

	collect(args.train)
	print "Done"
