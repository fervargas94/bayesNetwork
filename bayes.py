import itertools
import copy
import fileinput

class Node:
	def __init__(self, value, parents, childs, table):
		self.value = value
		self.parents = parents
		self.childs = childs
		self.table = table

	def __repr__(self):
		return "Node(%s %s %s %s)" % (self.value, self.parents, self.childs, self.table)


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


def getCombinations(given, parents):
	if type(given) != list:
		given = [given]
	if parents:
		total = []
		if len(parents) > 1:
			new = list(itertools.product(*((x, -x) for x in range(1, len(parents) + 1))))
			for i in new:
				arr = []
				for j in i:
					if j > 0:
						arr.append('+' + parents[j - 1])
					elif j != 0:
						arr.append('-' + parents[(-j) - 1])
				total.append(arr)
		else:
			total.append('+' + parents[0])
			total.append('-' + parents[0])

		return total
	else:
		return []

def getChainRule(combination, originalCombinations):
	total = 1.0
	#print("Combination", combination)
	if combination:
		search = combination[0]
		node = (filter(lambda x: x.value == search[1:] , bayesNetwork))
		values = search
		parents = node[0].parents
		if parents:
			for index, parent in enumerate(sorted(parents)):
				if index == 0:
					values += '|'
				if '+' + parent in originalCombinations:
					values += '+' + parent
				else:
					values += '-' + parent
				if index < len(parents) - 1:
					values += ","
		probabilities = node[0].table
		#print("Values", values)
		if values in probabilities:
			#print("Probability", values, probabilities[values])
			total = total * probabilities[values] * getChainRule(combination[1:], originalCombinations)
	return total

def parseNodes(nodes_array):
	nodes = []
	for value in nodes_array:
		for node in value:
			nodes.append(node)
	return nodes

def orderProbability(query, evidence):
	query = sorted(query.split(','), key=lambda x: x[1:])
	evidence = sorted(evidence.split(','), key=lambda x: x[1:])
	query = ",".join(query) + '|' + ",".join(evidence)
	return query

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
				if ch != "" and ch != '':
					parents.append(((ch[ch.find('|') + 1:ch.find('=')]).replace('+','').replace('-','')).split(','))
					given = float((ch[ch.find('=') + 1:]))
					givenProb = (ch[0:ch.find('=')])
					query = (givenProb[0:givenProb.find('|')]) 
					evidence = (givenProb[givenProb.find('|') + 1: ch.find('=')])
					probability[orderProbability(query, evidence)] = given
			
					if (ch[0:ch.find('|')]).count('+') > 0:
						query = (ch[0:ch.find('|')]).replace('+', '-') 
						evidence = (ch[ch.find('|') + 1: ch.find('=')])
						probability[orderProbability(query, evidence)] = round(1.0 - given, 2)
					else:
						query = (ch[0:ch.find('|')]).replace('-', '+') 
						evidence = (ch[ch.find('|') + 1: ch.find('=')])
						probability[orderProbability(query, evidence)] = round(1.0 - given, 2)
		else:
			probability = {}
			for ch in parent:
				if ch != "" and ch != '':
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

def parseQueries(bayesNetworkCopy):
	for query in queries:
		#print("-------------", query, "-------------")
		if query.count('|') > 0: 
			numerator = []
			numeratorParents = []
			denominator = []
			denominatorParents = []
			search = (query[:query.find('|')]).split(',')
			evidence = (query[query.find('|') + 1:]).split(',')
			for s in search:
				numerator.append(s[1:])
			for e in evidence:
				search.append(e)
				numerator.append(e[1:])
				denominator.append(e[1:])
			for n in numerator:
				matches = filter(lambda obj: obj.value == n, bayesNetworkCopy)
				parents = getParents(matches[0].parents)
				numeratorParents.append(parents)
				if n in denominator:
					denominatorParents.append(parents)
			numeratorParents = list(set(list(itertools.chain.from_iterable(numeratorParents))))
			denominatorParents = list(set(list(itertools.chain.from_iterable(denominatorParents))))
			numeratorParents = list(set(numeratorParents) - set(numerator))
			denominatorParents = list(set(denominatorParents) - set(denominator))
			upperCombinations = getCombinations(search, numeratorParents)
			downCombinations = getCombinations(evidence, denominatorParents)
			#print("given", search, evidence)
			upperSum = 0.0
			downSum = 0.0

			if upperCombinations:
				#print("len com", len(upperCombinations), upperCombinations)
				for com in upperCombinations:
					if type(com) != list:
						com = [com]
					probability = ",".join(search) + "," + ",".join(com)
					upperSum += getChainRule(list(set(probability.split(','))), list(set(probability.split(','))))
			else:
				upperSum += getChainRule(list(search), list(search))
			if downCombinations:
				#print("len com down", len(downCombinations), downCombinations)
				for com in downCombinations:
					if type(com) != list:
						com = [com]
					probability = ",".join(evidence) + "," + ",".join(com)
					downSum += getChainRule(list(set(probability.split(','))), list(set(probability.split(','))))
			else:
				downSum += getChainRule(list(evidence), list(evidence))
			#final_results.append(upperSum/downSum)
			print(('%.7f'%(upperSum/downSum)).rstrip('0'))
		else:
			matches = filter(lambda obj: obj.value == query.replace('+', '-').replace('-',''), bayesNetwork)
			if matches and query in matches[0].table:
				#final_results.append((matches[0].table)[query])
				print((matches[0].table)[query])
			else:
				given = query
				parents = getParents(matches[0].parents)
				combinations = getCombinations(given, parents)
				suma = 0.0
				for com in combinations:
					if type(com) != list:
						com = [com]
					suma += getChainRule([given] + com, [given] + com)
				#final_results.append(suma)
				print(('%.7f'%suma).rstrip('0'))


nodes = []
probabilities = []
queries = []
getting = 0
#input = fileinput.input()
bayesNetwork = []
final_results = []

for line in fileinput.input():
	if not line and getting == "q":
		break
	if getting == "n":
		if line != "" and line[0] != "[" and line[0] != "#" and line != "\n" and line != " " :
			nodes.append((((line.rstrip('\n').rstrip('\r')).replace(' ', '')).split(',')))
	if getting == "p":
		if line != "" and line[0] != "[" and line[0] != "#" and line != "\n" and line != " " :
			probabilities.append((line.rstrip('\n').rstrip('\r')).replace(' ', ''))
	if getting == "q":
		if line != "" and line[0] != "[" and line[0] != "#" and line != "\n" and line != " " :
			queries.append((line.rstrip('\n').rstrip('\r')).replace(' ', ''))
	if '[Probabilities]' in line:
		getting = "p"
	if '[Nodes]' in line:
		getting = "n"
	if '[Queries]' in line:
		getting = "q"

'''while 1:
	try:
		line = raw_input()
		if not line and getting == "q":
			break
		if getting == "n":
			if line != "" and line[0] != "[" and line[0] != "#":
				nodes.append((line.replace(' ', '')).split(','))
		if getting == "p":
			if line != "" and line[0] != "[" and line[0] != "#":
				probabilities.append((line.rstrip('\n')).replace(' ', ''))
		if getting == "q":
			if line != "" and line[0] != "[" and line[0] != "#":
				queries.append((line.rstrip('\n')).replace(' ', ''))
		if line == '[Probabilities]':
			getting = "p"
		if line == '[Nodes]':
			getting = "n"
		if line == '[Queries]':
			getting = "q"
	except (EOFError):
	   break #end of file reached'''

final_nodes = parseNodes(nodes)
parseProbabilities(final_nodes, probabilities)
bayesNetworkCopy = copy.deepcopy(bayesNetwork)
parseQueries(bayesNetworkCopy)





