#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# By Antoine Mazières -- http://ant1.cc/
# For CorText Project -- http://cortext.fr/
# CC-BY-CA
#
# 
# This script prints the content of the most frequent xpaths of a given webpage.
# So far, this is absolutely USELESS :(
# 

from lxml import etree
import urllib
import operator

#url = "http://www.perdu.com/"
url = 'http://www.lacuisinehelene.com/2012/02/pita-with-hummus-veggies-and-feta.html'
root = etree.HTML(urllib.urlopen(url).read())
d = {}

def print_path_of_elems(elem, elem_path=""):
    for child in elem:
        if not child.getchildren():
			full_path = "%s/%s" % (elem_path, child.tag)
			if d.has_key(full_path):
				d[full_path] = d.get(full_path, 0) + 1
			else:
				d[full_path] = 1			
        else:
            print_path_of_elems(child, "%s/%s" % (elem_path, child.tag))

print_path_of_elems(root, root.tag)
sorted_d = sorted(d.iteritems(), key=operator.itemgetter(1), reverse=True)

for each in sorted_d:
	print each
	i = 0
	slash_path = "/" + each[0]
	div = root.xpath(slash_path)
	while i <= (len(div) - 1):
		print div[i].text
		print '\n'
		i += 1