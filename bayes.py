import itertools
import fileinput

class Node:
	def __init__(self, value, parents, table):
		self.value = value
		self.parents = parents
		self.table = table

	def getValue(self):
		return self.val

	def __repr__(self):
		return "Node(%s %s %s)" % (self.value, self.parents, self.table)

def parseNodes(nodes_array):
	nodes = []
	for value in nodes_array:
		for node in value:
			nodes.append(node)
	return nodes

def parseProbabilities(nodes, probabilities):
	for node in nodes:
		child = (filter(lambda x: (x[0:x.find('|')]).count(node) > 0 , probabilities))
		childrens = []
		if len(child) > 1:
			probability = {}
			for ch in child:
				childrens.append(((ch[ch.find('|') + 1:ch.find('=')]).replace('+','').replace('-','')).split(','))
				given = float((ch[ch.find('=') + 1:]))
				probability[(ch[0:ch.find('=')])] = given
				if (ch[0:ch.find('|')]).count('+') > 0:
					probability[(ch[0:ch.find('|')]).replace('+', '-') + '|'  + (ch[ch.find('|') + 1: ch.find('=')])] = round(1.0 - given, 2)
				else:
					probability[(ch[0:ch.find('|')]).replace('-', '+') + '|'  + (ch[ch.find('|') + 1: ch.find('=')])] = round(1.0 - given, 2)
			bayesNetwork.append(Node(node, list(set(list(itertools.chain.from_iterable(childrens)))), probability))
		else:
			probability = {}
			for ch in child:
				given = float((ch[ch.find('=') + 1:]))
				probability[(ch[0:ch.find('=')])] = given
				if ch.count('+') > 0:
					probability[(ch[0:ch.find('=')]).replace('+', '-')] = round(1.0 - given, 2)
				else:
					probability[(ch[0:ch.find('=')]).replace('-', '+')] = round(1.0 - given, 2)
			bayesNetwork.append(Node(node, list(set(list(itertools.chain.from_iterable(childrens)))), probability))
		


nodes = []
probabilities = []
queries = []
getting = 0
input = fileinput.input()
bayesNetwork = []

for line in input:
	if not line and getting == "q":
		break
	if getting == "n":
		if line != "" and line[0] != "[" and line[0] != "#" and line != "\n":
			nodes.append((((line.rstrip('\n')).replace(' ', '')).split(',')))
	if getting == "p":
		if line != "" and line[0] != "[" and line[0] != "#" and line != "\n":
			probabilities.append((line.rstrip('\n')).replace(' ', ''))
	if getting == "q":
		if line != "" and line[0] != "[" and line[0] != "#" and line != "\n":
			queries.append((line.rstrip('\n')).replace(' ', ''))
	if line == '[Probabilities]\n':
		getting = "p"
	if line == '[Nodes]\n':
		getting = "n"
	if line == '[Queries]\n':
		getting = "q"

final_nodes = parseNodes(nodes)
parseProbabilities(final_nodes, probabilities)
for node in bayesNetwork:
	print(node)


