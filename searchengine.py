#!/usr/bin/env python3

import requests
import re
import argparse
import copy
import html.entities
##########################################
# Titres des parties pour parser la page #
##########################################

overview_titles = [
	"Standard Name",
	"Systematic Name",
	"SGD ID",
	"Aliases",
	"Feature Type",
	"Description",
	"Name Description",
	"", #il faut un symbole en plus qui n'est pas dans le texte pour finir la recherche (c'est sale)
	]

go_titles = [
	"Molecular Function",
	"Biological Process",
	"Cellular Component",
	"",
	]

########################### Convertit les codes HTML en symboles unicode #############################
html_pattern = re.compile("&([^;]+);")
 
def html_entity_decode_char(m):
	try:
		return html.entities.entitydefs[m.group(1)]
	except KeyError:
		return m.group(0)
 
def html_entity_decode(string):
	def sub(item):
		word = item.group(1)
		if len(word)>= 2 and word[0] == '#':
			try:
				if word[1] in ['x', 'X']:
					return chr(int(word[2:], 16))
				else:
					return chr(int(word[1:]))
			except ValueError:
				return item.group(0)
		elif word[0] != '#':
			return html_entity_decode_char(item)
		else:
			return item.group(0)
	return html_pattern.sub(sub, string)
######################################################################
# Code d'origine en python2.7 par Nit (porté en pyhton3 par Mikachu) #
######################################################################
#########################################################################################################

def cleanparenthesis(text):
	''' vire les infos entre parenthèses (exemple : (IDA))'''
	cleanr = re.compile('\(?[A-Z]{2,3}(\,|\))')
	cleantext = re.sub(cleanr,'',text)
	return cleantext

def cleanhtml(raw_html):
	'''transforme le html en texte'''
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

def cleanspace(texte):
	''' supprime une bonne partie des espaces inutiles'''
	cleanr = re.compile('[\s]{3,}')
	cleantext = re.sub(cleanr, '\n', texte)
	return cleantext

def get_info(texte):
	'''renvoie la liste des différentes parties'''
	cleanr = re.compile('<!--[\s\S]*?-->')
	cleantext = re.sub(cleanr, '$$$$$', texte)
	list_info = cleantext.split('$$$$$')
	list_info.pop(0)
	try :
		list_info.pop(-1)
	except :
		return None
	return list_info

def open_parse_input(i_file):
	'''ouvre le fichier csv de données et renvoie la liste des ORF'''
	file = open(i_file,"r")
	list_input=[]
	for line in file :
		if line != "":
			list_input.append(line.split("\n")[0])
	return list_input

def write_to_file_text(string):
	'''ecrit la string + \n dans le fichier '''
	if args.file :
		file = open(args.file+".csv","a")
		file.write(string)
		file.write("\n")
		file.close()

def write_to_file(overview,protein,go):
	'''Écrit dans le fichier de sortie'''
	if args.file :
		file = open(args.file+".csv","a")
		for i in overview:
			file.write(i)
			file.write(",")

		for i in go:
			if type(i)== list :
				if i != []:
					for j in i :
						if j != "":
							file.write(j)
							file.write(" ")
					file.write(",")
			else :
				file.write(i)
				file.write(",")
		file.write("\n")
		file.close()

def init_file():
	'''Initialise le fichier de sortie avec les titres'''
	write_to_file_text("sep=,")
	write_to_file(overview_titles[0:-2],[],go_titles[0:-2])

def makerequest(ORF):
	''' envoie la requete et retourne le contenu html de la page'''
	r = requests.get('http://yeastgenome.org/search?q='+ORF+'&is_quick=true')
	content = cleanhtml(r.text)
	return content

def parse_and_request(ORF):
	'''effectue la requête et la parse'''
	# dans le cas où on veut faire la requête sur yeastgenome
	if args.yeastgenome :
		infos_list = get_info(cleanspace(makerequest(ORF)))
		# Dans le cas où on a pas d'infos (la recherche n'a rien donné), on renvoie None
		if infos_list == None:
			return None
		#overview section 
		overview = infos_list[0]
		overview = overview.split('\n')
		overview_clean = []
		is_precedent = False
		overview_copy = copy.deepcopy(overview)
		for title in overview_titles :
			try :
				while overview_copy[0] != title :
					if is_precedent :
						# on vire les ; et les , parce-que c'est relou dans les CSV ...
						overview_clean.append((cleanparenthesis(html_entity_decode(overview_copy.pop(0)))).replace(",","").replace(";"," $"))
						is_precedent = False
					else :
						overview_copy.pop(0)
				overview_copy.pop(0)
				overview = copy.deepcopy(overview_copy)
				is_precedent = True
			except :
				overview_clean.append("")
				overview_copy = copy.deepcopy(overview)
				is_precedent = False

		#sequence section
		sequence = infos_list[1]
		sequence = sequence.split('\n')
		sequence_clean = [
		]
		#protein section
		protein = infos_list[2]
		protein = protein.split('\n')
		protein_clean = [
			[],	#length (a.a.)
			[],	#mol. weigth (Da)
			[],	#isoelectric point
		]
		#go section
		go = infos_list[3]
		go = go.split('\n')
		go_copy = copy.deepcopy(go)
		go_clean = [
			[],
			[], #molecular function
			[], #biological process
			[],	#cellular component
		] 
		is_precedent = False
		for a, title in enumerate(go_titles) :
			try :
				while go_copy[0] != title :
					if is_precedent :
						# on vire les ; et les , parce que c'est relou dans les CSV ...
						go_clean[a].append((cleanparenthesis(html_entity_decode(go_copy.pop(0)))).replace(","," $").replace(";","PVIRG").replace("Manually Curated",""))
					else :
						go_copy.pop(0)
				go_copy.pop(0)
				go = copy.deepcopy(go_copy)
				is_precedent = True
			except :
				print("Pas d'infos sur :",title)
				go_clean[a].append("")
				go_copy = copy.deepcopy(go)
				is_precedent = False

		#pathway section
		pathway = infos_list[4]
		#phenotype section
		phenotype = infos_list[5]
		#interaction section
		interaction = infos_list[6]
		#regulation section
		regulation = infos_list[7]
		#expression section
		expression = infos_list[8]
		#paragraph section
		paragrah = infos_list[9]
		#litterature section
		litterature = infos_list[10]
		#history section
		history = infos_list[11]
		#references section
		references = infos_list[12]
	return overview_clean,protein_clean,go_clean


############## Là on récupère les arguments passés au script ###################

parser = argparse.ArgumentParser(description='Search for the specified ORF on the yeastgenome.org database')
parser.add_argument('-y','--yeastgenome',help='Make the request on yeastgenome.org', action='store_true')
parser.add_argument('-o','--orf', help='ORF', type=str)
parser.add_argument('-f','--file',help='Write the output of the script to the selected file', type=str)
parser.add_argument('-i','--input',help='Get the ORF from a csv input file', type=str)
parser.add_argument('-r','--rank',help='Set the starting rank', type=int)
args = parser.parse_args()

############## Et là on réagi en fonction de ces arguments #####################

if args.orf :
	parse_and_request(args.orf)

if args.input :
	count_input=1
	list_input = open_parse_input(args.input)
	total_input = len(list_input)
	list_erreurs = []
	count_errors = 0
	if args.rank :
		pass
	else :
		init_file()
	preced_input = None
	for orf_input in list_input :
		print(count_input,"(",count_errors,")","/",total_input)
		if args.rank == None or count_input >= args.rank:
			if orf_input != preced_input:
				result=parse_and_request(orf_input)
				if result != None:
					overview,protein,go = result
					write_to_file(overview,protein,go)
				else :
					print("Erreur sur : ",orf_input)
					list_erreurs.append(orf_input)
					count_errors+=1
		count_input+=1
		preced_input = orf_input		