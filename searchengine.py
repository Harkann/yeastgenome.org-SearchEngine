#!/usr/bin/env python3

import requests
import re
import argparse


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def cleanspace(texte):
    cleanr = re.compile('[\r\t\f\v ]{3,}')
    cleantext = re.sub(cleanr, '', texte)
    cleanr = re.compile('\n{3,}')
    cleantext = re.sub(cleanr, '', cleantext)
    return cleantext

def get_info(texte):
    cleanr = re.compile('<!--[\s\S]*?-->')
    cleantext = re.sub(cleanr, '$$$$$', texte)
    list_info = cleantext.split('$$$$$')
    list_info.pop(0)
    list_info.pop(-1)
    return list_info

def makerequest(ORF):
    r = requests.get('http://yeastgenome.org/search?q='+ORF+'&is_quick=true')
    content = cleanhtml(r.text)
    return content

parser = argparse.ArgumentParser(description='Search for the specified ORF on the yeastgenome.org database')
parser.add_argument('-y','--yeastgenome',help='Make the request on yeastgenome.org', action='store_true')
parser.add_argument('orf', help='ORF', type=str)
args = parser.parse_args()
if args.orf :
    content = makerequest(args.orf)
    print(get_info(cleanspace(content)))
