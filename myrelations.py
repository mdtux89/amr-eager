#used for np extraction...

from collections import defaultdict
import copy

class MyRelations:
   
	def __init__(self, initial):
		self.children = defaultdict(list)
		self.parents = defaultdict(list)
		self.maps = {}
		for r in initial:
			self.add(r[0],r[1],r[3],r[4],r[2])

	def add(self, node1, c1, node2, c2, label):
		self.maps[node1] = c1
		self.maps[node2] = c2
		if (node2,label) not in self.children[node1]:
			self.children[node1].append((node2,label))
		if (node1,label) not in self.parents[node2]:
			self.parents[node2].append((node1,label))

	
	def dfs(self, root, visited):
		lst = []
		for (child,label) in self.children[root]:
			lst.append((root,self.maps[root],label,child,self.maps[child]))
			if child not in visited:
				visited.append(child)
				lst.extend(self.dfs(child,visited))
		return lst

	def _isConnToRoot(self, node, visited):
		if node in visited:
			return False
		visited.append(node)

		if node == "TOP":
			return True
		for (father,_) in self.parents[node]:
			if self._isConnToRoot(father, visited):
				return True
		return False

	def triples(self):
		root = "TOP"
		for node in copy.deepcopy(self.children):
			if node is None:
				continue
			if self._isConnToRoot(node, []) == False and len(self.children[node]) > 0:
				self.add("TOP", "", node, self.maps[node], ":top")
		
		lst = self.dfs(root,[])

		if len(self.children[root]) > 1:
			counter = 1
			lst2 = []
			lst2.append(("TOP","",":top","mu","multi-sentence"))
			for (v1,c1,l,v2,c2) in lst:
				if v1 == "TOP":
					v1 = "mu"
					c1 = "multi-sentence"
					l = ":snt" + str(counter)
					counter += 1
				lst2.append((v1,c1,l,v2,c2))
			return lst2
		return lst
