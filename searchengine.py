#!/usr/bin/env python3

import requests
import re

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
def makerequest(ORF):
    r = requests.get('http://yeastgenome.org/search?q='+ORF+'&is_quick=true')
    content = cleanhtml(r.text)
    return content

content = makerequest('YPR139C')
list_content = 
print(cleanspace(content).split('\n'))
