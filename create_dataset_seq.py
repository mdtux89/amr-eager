import cPickle as pickle
from transition_system import TransitionSystem
from state import State
from embs import Embs
from oracle import Oracle
from graphlet import Graphlet
import propbank
import copy
import insertzeros
from resources import Resources

Resources.init_table(False)
# Resources.init_token_gl_keys(False)
Resources.init_probs(False)
# Resources.init_token_gl_counts(len(Resources.tokens.keys()), len(Resources.graphlets.keys()), False)

prefix = "ldc_devset_sentences.txt"
print "Loading data.."
alltokens = pickle.load(open(prefix + ".tokens.p", "rb"))
alldependencies = pickle.load(open(prefix + ".dependencies.p", "rb"))
allalignments = pickle.load(open(prefix + ".alignments.p", "rb"))
allrelations = pickle.load(open(prefix + ".relations.p", "rb"))
print "Number of sentences ", len(alltokens)

labels = {}
labels_counter = 1
for line in open("resources/relations.txt"):
	labels[line.strip()] = labels_counter
	labels_counter += 1

# graphlets = [i for i,_ in enumerate(pickle.load(open("resources/graphlets.p", "rb")))]

dataset = open("/disk/scratch/s1333293/dataset.txt","w")
dep_seq = open("/disk/scratch/s1333293/dep_seq.txt","w")
word_seq = open("/disk/scratch/s1333293/word_seq.txt","w")
targets = open("/disk/scratch/s1333293/targets.txt","w")

counter = 0
depth = 2
embs = Embs()
for tokens, dependencies, alignments, relations in zip(alltokens, alldependencies, allalignments, allrelations):
	counter += 1
	print "Sentence no: ", counter
	data = (tokens, dependencies, relations, alignments)
	t = TransitionSystem(embs, data, depth, "TRAIN", 0)
	for feats, action in t.statesactions():
		if action != None and action.name.startswith("shift"):
			continue
		else:
			f_rel, f_lab = feats
                        for v in f_rel[0]:
                                dataset.write(str(v)+",")
			if action != None and action.name == "lrel":
                                #lrel
                                dataset.write(str(1) + "\n")
                        elif action != None and action.name == "rrel":
                                #rrel
                                dataset.write(str(2) + "\n")
                        else:
                                assert(action == None)
                                #nothing
                                dataset.write(str(3) + "\n")

			dep_seq.write(str(f_rel[1][0]))
			for v in f_rel[1][1:]:
		 		dep_seq.write("," + str(v))
		 	dep_seq.write("\n")

		 	word_seq.write(str(f_rel[2][0]))
		 	for v in f_rel[2][1:]:
		 		word_seq.write("," + str(v))
		 	word_seq.write("\n")

		 	if action != None and action.name == "lrel":
		 		targets.write(str(1) + "\n")
		 	elif action != None and action.name == "rrel":
		 		targets.write(str(2) + "\n")
		 	else:
		 		assert(action == None)
		 		targets.write(str(3) + "\n")

# insertzeros.run("/disk/scratch/s1333293/word_seq.txt")
# insertzeros.run("/disk/scratch/s1333293/dep_seq.txt")
print "Done"

