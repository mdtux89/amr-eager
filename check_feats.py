
dict_f = {}
print "Training.."
for line in open("state_feats_training.txt"):
	f = line.split(" ---- ")
	if f[0] not in dict_f:
		dict_f[f[0]] = []
	dict_f[f[0]].append(f[1])

print "Parsing.."
for line in open("state_feats_parsing.txt"):
	f = line.split(" ---- ")
	if f[0] in dict_f and f[1] not in dict_f[f[0]]:
		print f[0]
		print f[1]
		print dict_f[f[0]]
		raw_input()
 	#assert(f[0] not in dict or f[1] == dict[f[0]])

print "Done"

