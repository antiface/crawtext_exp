#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# By Antoine Mazières -- http://ant1.cc/
# For CorText Project -- http://cortext.fr/
# CC-BY-CA
#
# 
# This script prints the xpath nodes with the more content
# So far, this is not so USELESS :) to be fine-tunned !
# 

from lxml import etree
import urllib
import operator
import re

#url = "http://www.perdu.com/"
#url = 'http://www.lacuisinehelene.com/2012/02/pita-with-hummus-veggies-and-feta.html'
url ='http://www.lexpress.fr/actualite/sciences/sante/la-bonne-algue-verte_489903.html'
url ='http://www.capital-terrain.fr/#'
root = etree.HTML(urllib.urlopen(url).read())

### SAMPLE HTML 4 DEBUG
# root = etree.HTML('''
# <html>
# <head>
# <title>Vous Etes Perdu ?</title>
# </head>
# <body>
# <h3></h3>
# <h1>Perdu sur l'Internet ?</h1>
# <h1>Perdu dans la vie ?</h1>
# <h2>Pas de panique, on va vous aider</h2>
# <strong><pre>    * <----- vous &ecirc;tes ici</pre></strong></body></html>
# ''')
d = {}

def print_path_of_elems(elem, elem_path=""):
    for child in elem:
        if not child.getchildren() and child.text:
			full_path = "/%s/%s" % (elem_path, child.tag)
			if d.has_key(full_path):
				d[full_path] += [len(child.text)]
			else:
				d[full_path] = [len(child.text)]		
        else:
            print_path_of_elems(child, "%s/%s" % (elem_path, child.tag))

print_path_of_elems(root, root.tag)
sorted_d = sorted(d.iteritems(), key=operator.itemgetter(1), reverse=True)

max_len = sorted_d[0][1][0]
print max_len

for each in sorted_d:
	#This IF is a random guess: needs more example to find a better way to select top of the dict
#	if each[1][0] > (max_len / 2):
	last_tag = each[0].split('/')[-1]
	match = re.search('\<.*\>',last_tag)
	if not match and last_tag not in ['style','script']:
		print "***xpath: %s" % each[0]
		total = 0
		for num in each[1]:
			total += num
		print "***average_length: %d" % (total/len(each[1]))
		for path in root.xpath(each[0]):
			i = 0
			print "\n%s\n" % path.text
