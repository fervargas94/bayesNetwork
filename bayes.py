import itertools
import fileinput

class Node:
	def __init__(self, value, parents, childs, table):
		self.value = value
		self.parents = parents
		self.childs = childs
		self.table = table

	def getParentNodes(self):
		return self.parents

	def __repr__(self):
		return "Node(%s %s %s %s)" % (self.value, self.parents, self.childs, self.table)

def parseNodes(nodes_array):
	nodes = []
	for value in nodes_array:
		for node in value:
			nodes.append(node)
	return nodes

def getParents(parents):
	for parent in parents:
		if parent:
			matches = filter(lambda obj: obj.value == parent, bayesNetwork)
			if matches:
				for match in matches:
					if len(match.parents) > 0:
						for parent in match.parents:
							if parent not in parents:
								parents.append(parent)
	return parents

def parseQueries():
	for query in queries:
		if query.count('|') > 0: 
			search = query[:query.find('|')]
			evidence = query[query.find('|') + 1:]
		else:
			matches = filter(lambda obj: obj.value == query.replace('+', '-').replace('-',''), bayesNetwork)
			if matches and query in matches[0].table:
				print((matches[0].table)[query])
			else:
				given = query
				parents = getParents(matches[0].parents)
				combinations = getCombinations(given, parents)
				suma = 0.0
				for com in combinations:
					suma += getChainRule(com)
				print(suma)

def getCombinations(given, parents):
	total = []
	if len(parents) > 1:
		new = list(itertools.product(*((x, -x) for x in range(1, len(parents) + 1))))
		for i in new:
			arr = [given]
			for j in i:
				if j > 0:
					arr.append('+' + parents[j - 1])
				elif j != 0:
					arr.append('-' + parents[(-j) - 1])
			total.append(arr)
	else:
		arr = [given]
		arr.append('+' + parents[0])
		total.append(arr)
		arr = [given]
		arr.append('-' + parents[0])
		total.append(arr)

	return total

def getChainRule(combination):
	total = 1.0
	if combination:
		values = combination[0]
		for value in combination:
			valueCopy = value[1:]
			node = (filter(lambda x: x.value == valueCopy , bayesNetwork))
			parents = node[0].parents
			if parents:
				for index, parent in enumerate(sorted(parents)):
					if index == 0:
						values += '|'
					if '+' + parent in combination:
						values += '+' + parent
					else:
						values += '-' + parent
					if index != len(parents) - 1:
						values += ","
			probabilities = node[0].table
			if values in probabilities:
				total = total * probabilities[values] * getChainRule(combination[1:])
	return total



def parseProbabilities(nodes, probabilities):
	for node in nodes:
		#Obtain the probabilities where the node is in the first side
		parent = (filter(lambda x: (x[0:x.find('|')]).count(node) > 0 , probabilities))
		#Obtain the probabilities where the node is in the second side
		children = (filter(lambda x: (x[x.find('|') + 1:x.find('=')]).count(node) > 0 , probabilities))
		parents = []
		childrens = []
		if len(parent) > 1:
			probability = {}
			for ch in parent:
				parents.append(((ch[ch.find('|') + 1:ch.find('=')]).replace('+','').replace('-','')).split(','))
				given = float((ch[ch.find('=') + 1:]))
				probability[(ch[0:ch.find('=')])] = given
				if (ch[0:ch.find('|')]).count('+') > 0:
					probability[(ch[0:ch.find('|')]).replace('+', '-') + '|'  + (ch[ch.find('|') + 1: ch.find('=')])] = round(1.0 - given, 2)
				else:
					probability[(ch[0:ch.find('|')]).replace('-', '+') + '|'  + (ch[ch.find('|') + 1: ch.find('=')])] = round(1.0 - given, 2)
		else:
			probability = {}
			for ch in parent:
				given = float((ch[ch.find('=') + 1:]))
				probability[(ch[0:ch.find('=')])] = given
				if ch.count('+') > 0:
					probability[(ch[0:ch.find('=')]).replace('+', '-')] = 1.0 - given
				else:
					probability[(ch[0:ch.find('=')]).replace('-', '+')] = 1.0 - given
		if len(children) > 1:
			for ch in children:
				#If the probabilty does not contain | then ignore it 
				if ch.find('|') > -1:
					childrens.append((ch[0:ch.find('|')].replace('+','').replace('-','')).split(','))
					
		bayesNetwork.append(Node(node, list(set(list(itertools.chain.from_iterable(parents)))), list(set(list(itertools.chain.from_iterable(childrens)))),probability))


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
for val in bayesNetwork:
	print(val.table)
parseQueries()


