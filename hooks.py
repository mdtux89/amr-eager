#!/usr/bin/env python
#coding=utf-8

'''
Defines the hooks for the different type of named entities.

@author: Marco Damonte (m.damonte@sms.ed.ac.uk)
@since: 03-10-16
'''

import re
from node import Node
from collections import defaultdict
try:
        from counter import Counter
except:
        from collections import Counter

#resources
wikis = {}
for item in open("resources/countries.txt").read().splitlines():
	wikis[item.split(",")[0].strip()] = item.split(",")[1].strip()

countries = wikis.keys()

nationalities = {}
for item in open("resources/nationalities.txt").read().splitlines():
	c = ""
	for i in item.split(" => ")[0].strip()[1:-1].split():
		i = i[0].upper() + i[1:]
		c += i + " "
	c = c.strip()
	nationalities[item.split(" => ")[1].strip()[1:-2].lower()] = c

for item in open("resources/nationalities2.txt").read().splitlines():
	if item.split("\t")[0] not in nationalities:
		nationalities[item.split("\t")[1].lower()] = item.split("\t")[0]

states = [item.strip() for item in open("resources/states.txt").read().splitlines()]

cities = [item.strip() for item in open("resources/cities.txt").read().splitlines()]

organizations = defaultdict(list)
for line in open("resources/organizations.txt"):
	fields = line.strip().split()
	if len(fields) > 1:
		organizations[fields[0]] = fields[1]
##

def names(name_type, cat, token, var, variables):
	nodes = []
	relations = []
	v1 = variables.nextVar()
	v2 = variables.nextVar()
	ntop = Node(token, v1, cat, False)
	nodes.append(ntop)
	nname = Node(token, v2, "name", False)
	nodes.append(nname)
	relations.append((ntop, nname , ":name"))
	if var in wikis and wikis[var] != "":
		nwiki = Node(token, '"' + wikis[var] + '"', name_type, True)
		if wikis[var] != var:
			nodes.append(nwiki)
	else:
		nwiki = Node(token, '"' + var + '"', name_type, True)
	relations.append((ntop, nwiki , ":wiki"))
	for i, word in enumerate(var.split("_")):
		nop = Node(token, '"' + word + '"', name_type, True)
		nodes.append(nop)
		relations.append((nname, nop , ":op" + str(i + 1)))
	return (nodes, relations)

def isState(name):
	name = name.strip()
	name.replace("'","")
	name.replace('"','')
	if name in states:
		return name
	return None

def isCity(name):
	name = name.strip()
	name.replace("'","")
	name.replace('"','')
	if name in cities:
		return name
	return None

def isOrg(name):
	name = name.strip()
	name.replace("'","")
	name.replace('"','')
	if name in organizations:
		return organizations[name]
	return None

def isCountry(name):
	name = name.strip()
	name = name.replace("'","")
	name = name.replace('"','')
	if name.startswith("_"):
		name = name[1:]
	if name.endswith("_"):
		name = name[:-1]
	name = name.replace("__","_")
	if name in countries:
		return name
	name = name.replace(".","")
	for c in countries:
		if "".join([d[0].lower() for d in c.split("_")]) == name.lower():
			return c
	for c in countries:
		if name.lower() in [d.lower() for d in c.split("_")]:
			return c
	if name.startswith("the_") or name.startswith("The_"):
		name = name[4:]
	 	return isCountry(name)
	return None

def stripzeros(num):
	return num.lstrip("0")

def run(token, var, label, variables):

	if label == "DATE" and re.match("^(\d{4}|XXXX)(-\d{2})?(-\d{2})?$",token.word):
		nodes = []
		relations = []
		v1 = variables.nextVar()
		ntop = Node(token, v1, "date-entity", False)
		nodes.append(ntop)
		if len(token.word.split("-")) == 3:
			nday = Node(token, stripzeros(token.word.split("-")[2]), label, True)
			nmonth = Node(token, stripzeros(token.word.split("-")[1]), label, True)
			nodes.append(nday)
			nodes.append(nmonth)
			relations.append((ntop, nday , ":day"))
			relations.append((ntop, nmonth , ":month"))
			if token.word.split("-")[0] != "XXXX":
				nyear = Node(token, token.word.split("-")[0], label, True)
				nodes.append(nyear)
				relations.append((ntop, nyear , ":year"))

		elif len(token.word.split("-")) == 2:
			nmonth = Node(token, stripzeros(token.word.split("-")[1]), label, True)
			nodes.append(nmonth)
			relations.append((ntop, nmonth , ":month"))
			if token.word.split("-")[0] != "XXXX":
				nyear = Node(token, token.word.split("-")[0], label, True)
				nodes.append(nyear)
				relations.append((ntop, nyear , ":year"))
			
		elif len(token.word.split("-")) == 1:
			nyear = Node(token, token.word.split("-")[0], label, True)
			nodes.append(nyear)
			relations.append((ntop, nyear , ":year"))
		return (nodes,relations)

	if label == "LOCATION":
		state = isState(token.word)
		if state:
			return names(label, "state", token, var, variables)
	 	country = isCountry(token.word)
	 	if country != None:
	 		return names(label, "country", token, var, variables)
	 	city = isCity(token.word)
	 	if city != None:
	 		return names(label, "city", token, var, variables)
		return False
	if var.lower() in nationalities:
		return names(label, "country", token, nationalities[var.lower()], variables)
	if label == "PERSON":
	 	return names(label, "person", token, var, variables)
	if label == "ORGANIZATION":
		org_type = isOrg(token.word)
		if org_type != None:
	   		return names(label, org_type, token, var, variables)
	   	return False

	if label == "ORDINAL":
		nodes = []	
		relations = []
		v1 = variables.nextVar()
		n1 = Node(token, v1, "ordinal-entity", False)
		n2 = Node(token, var.split(".")[0], "ORDINAL", True)
		nodes.append(n1)
		nodes.append(n2)
		relations.append((n1, n2, ":value"))
		return (nodes, relations)

	if label =="PERCENT":
		nodes = []
		relations = []
		v1 = variables.nextVar()
		n1 = Node(token, v1, "percentage-entity", False)
		n2 = Node(token, var.split("_")[0], label, True)
		nodes.append(n1)
		nodes.append(n2)
		relations.append((n1, n2, ":value"))
		return (nodes, relations)	

	if label == "NUMBER" and var.replace(".","").isdigit():
		nodes = []
		relations = []
		n1 = Node(token, var, "NUMBER", True)
		nodes.append(n1)
		return (nodes, relations)		
	 	return percentage(token, var, variables)

	if label =="MONEY":
		nodes = []
		relations = []
		v1 = variables.nextVar()
		v2 = variables.nextVar()
		n1 = Node(token, v1, "monetary-quantity", False)
		n3 = Node(token, v2, var.split("_")[1], False)
		n2 = Node(token, var.split("_")[0], label, True)
		nodes.append(n1)
		nodes.append(n2)
		nodes.append(n3)
		relations.append((n1, n2, ":quant"))
		relations.append((n1, n3, ":unit"))
		return (nodes, relations)	

	return False
