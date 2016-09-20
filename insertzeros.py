import shutil

def run(filename):
	tmp = open("filetmp.txt","w")
	lenseq = 0
	for line in open(filename):
		l = len(line.split(",")) - 1
		if l > lenseq:
			lenseq = l

	for line in open(filename):
		diff = lenseq - (len(line.split(",")) - 1)
		for i in range(0, diff):
			tmp.write("0,")
		tmp.write(line.strip() + "\n")

	tmp.close()
	shutil.move("filetmp.txt", filename)
