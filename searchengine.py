#!/usr/bin/env python3

import requests
import re
import argparse
import copy

overview_titles = [
	"Standard Name",
	"Systematic Name",
	"SGD ID",
	"Aliases",
	"Feature Type",
	"Description",
	"Name Description",
	"",
	]

go_titles = [
	"Molecular Function",
	"Biological Process",
	"Cellular Component",
	"",
	]

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
	file = open(i_file,"r")
	list_input=[]
	for line in file :
		if line != "":
			list_input.append(line.split("\n")[0])
	return list_input


def write_to_file(overview,protein,go):
	if args.file :
		file = open(args.file+".csv","a")
		for i in overview:
			file.write(i)
			file.write(",")
		for i in go:
			if type(i)== list :
				if i != []:
					for j in i :
						file.write(j)
						file.write("$")
			else :
				file.write(i)
			file.write(",")
		file.write("\n")
		file.close()

def init_file():
	write_to_file(overview_titles,[],go_titles)


def makerequest(ORF):
	''' envoie la requete et retourne le contenu html de la page'''
	r = requests.get('http://yeastgenome.org/search?q='+ORF+'&is_quick=true')
	content = cleanhtml(r.text)
	return content

def parse_and_request(ORF):
	if args.yeastgenome :
		infos_list = get_info(cleanspace(makerequest(ORF)))
		if infos_list == None:
			return None
		i = 0
		#overview section 
		overview = infos_list[0]
		overview = overview.split('\n')
		overview_clean = []
		is_precedent = False
		overview_copy = copy.deepcopy(overview)
		for title in overview_titles :
			try :
				while overview_copy[i] != title :
					if is_precedent :
						# on vire les ; et les , parceque c'est relou dans les CSV ...
						overview_clean.append((overview_copy.pop(0)).replace(",","$").replace(";","$"))
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
			[],
			[],
			[],
		]
		"""
		protein_clean = [
			protein[8],	 #length (a.a.)
			protein[10],	#mol. weigth (Da)
			protein[12],	#isoelectric point
		]
		"""
		#go section
		go = infos_list[3]
		go = go.split('\n')
		go_copy = copy.deepcopy(go)
		go_clean = [
			[],
			[], #molecular function
			[], #biological process
			[]] #cellular component
		is_precedent = False
		for a, title in enumerate(go_titles) :
			
			try :
				while go_copy[i] != title :
					if is_precedent :
						# on vire les ; et les , parce que c'est relou dans les CSV ...
						go_clean[a].append((go_copy.pop(0)).replace(",","$").replace(";","$").replace("Manually Curated",""))
					else :
						go_copy.pop(0)
				go_copy.pop(0)
				go = copy.deepcopy(go_copy)
				is_precedent = True
			except :
				print("Va niquer ta mère")
				go_clean.append("")
				go_copy = copy.deepcopy(go)
				is_precedent = False

		#pathway section
		pathway = infos_list[4]
		#phenotype section
		phenotype = infos_list[5]
		phenotype = phenotype.split('\n')
		
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



#
#
#
#
#



parser = argparse.ArgumentParser(description='Search for the specified ORF on the yeastgenome.org database')
parser.add_argument('-y','--yeastgenome',help='Make the request on yeastgenome.org', action='store_true')
parser.add_argument('-o','--orf', help='ORF', type=str)
parser.add_argument('-f','--file',help='Write the output of the script to the selected file', type=str)
parser.add_argument('-i','--input',help='Get the ORF from a csv input file', type=str)
args = parser.parse_args()


if args.orf :
	parse_and_request(args.orf)

if args.input :
	count_input=1
	list_input = open_parse_input(args.input)
	total_input = len(list_input)
	init_file()
	preced_input = None
	for orf_input in list_input :
		print(count_input,"/",total_input)
		if orf_input != preced_input:
			result=parse_and_request(orf_input)
			if result != None:
				overview,protein,go = result
				write_to_file(overview,protein,go)
				
			else :
				print("Erreur sur : ",orf_input)
			count_input+=1
			preced_input = orf_input

			