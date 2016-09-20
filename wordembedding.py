import re
import string
from nltk import pos_tag

class WordEmbedding:
	def __init__(self, filename, dim, punct, unk, root):
		self.embeddings = {}
		self.embeddings_pos = {}
		self.embeddings_coarse = {}
		self.embeddings_label = {}
		self.oov = []
		for line in open(filename):
			v = line.split()
			self.embeddings[v[0]] = v[1:]
		self.punct = punct
		self.unk = unk
		self.root = root
		self.dim = dim

	def _preprocess(self, word):
		reg = re.compile(".+-[0-9][0-9]")
		word = word.strip().lower()
		if reg.match(word) != None:
			word = word.split("-")[0]
		#word = word.replace("-","-")
		word = word.replace("0","zero")
		word = word.replace("1","one")
		word = word.replace("2","two")
		word = word.replace("3","three")
		word = word.replace("4","four")
		word = word.replace("5","five")
		word = word.replace("6","six")
		word = word.replace("7","seven")
		word = word.replace("8","eight")
		word = word.replace("9","nine")
		return word

	def get(self, word, pos):
		if pos == "TOP":
			return self.root

		word = self._preprocess(word)
		if word not in self.embeddings and word in list(string.punctuation):
			return self.punct
		elif word in self.embeddings:
			return self.embeddings[word]
		else:
			if pos in self.embeddings:
				return self.embeddings[pos]
			self.oov.append(word)
			return self.unk

			
	def OOV(self):
		return len(self.oov)
