#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# By Antoine Mazières -- http://ant1.cc/
# For CorText Project -- http://cortext.fr/
# CC-BY-CA
#
# 
# This script prints the xpath nodes with the more content
# So far, this is absolutely USELESS :(
# 

from lxml import etree
import urllib
import operator
import re

#url = "http://www.perdu.com/"
# url = 'http://www.lacuisinehelene.com/2012/02/pita-with-hummus-veggies-and-feta.html'
# root = etree.HTML(urllib.urlopen(url).read())
root = etree.HTML('''
<html>
<head>
<title>Vous Etes Perdu ?</title>
</head>
<body>
<h3></h3>
<h1>Perdu sur l'Internet ?</h1>
<h1>Perdu dans la vie ?</h1>
<h2>Pas de panique, on va vous aider</h2>
<strong><pre>    * <----- vous &ecirc;tes ici</pre></strong></body></html>
''')
d = {}

# dict path,length
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
# print sorted_d

# dict path,average_lenght
for each in sorted_d:
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
