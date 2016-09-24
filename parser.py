import argparse
import cPickle as pickle
from transition_system import TransitionSystem
import src.amr
import copy
from embs import Embs
from resources import Resources

argparser = argparse.ArgumentParser(description='Process some integers.')
argparser.add_argument("-s", "--stdout", help="Print results on stdout", action='store_true')
argparser.add_argument("-c", "--comments", help="Print sentence and sentence's id before graph", action='store_true')
argparser.add_argument("-o", "--oracle", help="Run in oracle mode", action='store_true')
argparser.add_argument("-v", "--verbose", help="Print status information", action='store_true')
argparser.add_argument("-f", "--file", help="Input file", required = True)
argparser.add_argument("-m", "--model", help="Model directory", default="resources/")
try:
    args = argparser.parse_args()
except:
    argparser.error("Invalid arguments")
    sys.exit(0)

Resources.init_table(False)

prefix = args.file
alltokens = pickle.load(open(prefix + ".tokens.p", "rb"))
alldependencies = pickle.load(open(prefix + ".dependencies.p", "rb"))
embs = Embs()
if args.oracle == False:
	i = 0
	if args.stdout == False:
		fw = open("output.txt","w")
	TransitionSystem.load_model(args.model)
	for tokens, dependencies in zip(alltokens, alldependencies):
	 	i += 1
	 	if args.verbose:
	 		print "Sentence", i
	 	if args.comments:
		 	if args.stdout == False:
			 	fw.write("# ::snt " + " ".join([t.word for t in tokens]) + "\n")
			 	fw.write("# ::id " + str(i) + "\n")
			else:
			 	print "# ::snt " + " ".join([t.word for t in tokens])
			 	print "# ::id " + str(i)
	 	data = (copy.deepcopy(tokens), copy.deepcopy(dependencies))
		t = TransitionSystem(embs, data, "PARSE", 2)
	 	triples = t.relations()
	 	if triples != []:
	 		graph = src.amr.AMR.triples2String(triples)
	 		if str(graph).startswith("(") == False:
	 			graph = "(tmp / " + str(graph) + ")"
	 		if args.stdout == False:
	 			fw.write(str(graph) + "\n" + "\n")
	 		else:
	 			print str(graph)
	 			print ""
	 	else:
	 		if args.stdout == False:
	 			fw.write("(v / emptygraph)" + "\n" + "\n")
	 		else:
	 			print "(v / emptygraph)"
	 			print ""
	if args.stdout == False:
		fw.close()

else:
	allalignments = pickle.load(open(prefix + ".alignments.p", "rb"))
	allrelations = pickle.load(open(prefix + ".relations.p", "rb"))
	allalignlines = open(prefix + ".alignments").read().splitlines()
	i = 0
	if args.stdout == False:
		fw = open("oracle_exp.txt","w")
	#TransitionSystem.load_model(args.model)
	for tokens, dependencies, alignments, relations in zip(alltokens, alldependencies, allalignments, allrelations):
		i += 1
		if args.verbose:
			print "Sentence", i
                data = (copy.deepcopy(tokens), copy.deepcopy(dependencies), copy.deepcopy(relations), copy.deepcopy(alignments))
                t = TransitionSystem(embs, data, "ORACLETEST", 0)
                triples = t.relations()
                if args.comments:
                        if args.stdout == False:
                                fw.write("# ::snt " + " ".join([t.word for t in tokens]) + "\n")
                                fw.write("# ::id " + str(i) + "\n")
				fw.write("# ::alignments " + allalignlines[i - 1] + "\n")
                        else:
                                print "# ::snt " + " ".join([t.word for t in tokens])
                                print "# ::id " + str(i)
				print "# ::alignments " + allalignlines[i - 1]
		if triples != []:
			graph = src.amr.AMR.triples2String(triples)
			if str(graph).startswith("(") == False:
				graph = "(tmp / " + str(graph) + ")"
			if args.stdout == False:
				fw.write(str(graph) + "\n" + "\n")
			else:
				print str(graph)
				print ""
		else:
			if args.stdout == False:
				fw.write("(v / emptygraph)" + "\n" + "\n")
			else:
				print "(v / emptygraph)"
				print ""
	if args.stdout == False:
		fw.close()
