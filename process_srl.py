
def process_srl(filename):
	print filename
	allroles = []
	sents = open(filename).read()
	for sentence in sents.split("----\n"):
		sentence = sentence.strip()
		print sentence
		if sentence.strip() == "":
			break
		sentence = sentence.split("\n")
		n_verbs = len(sentence[0].split("\t")) - 2
		verbs = []
		roles = []
		for i, line in enumerate(sentence):
			line = line.split("\t")
			line[1] = line[1].strip()
			if line[1] != "-":
				verbs.append(i)
		assert(len(verbs) == n_verbs)
		# if len(verbs) != n_verbs:
		# 	print "SRL VERBS MISMATCH!"
		# 	raw_input()
		# else:
		for i, line in enumerate(sentence):
			line = line.split("\t")
			for k in range(2,len(line)):
				line[k] = line[k].strip()
				if line[k] != "O" and i != verbs[k - 2]:
					roles.append((i,line[k],verbs[k - 2]))
		allroles.append(roles)
		print roles
		raw_input()
	return allroles
