#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# By Antoine Mazières -- http://ant1.cc/
# For CorText Project -- http://cortext.fr/
# CC-BY-CA
#
# Needs libxml2 from http://xmlsoft.org/python.html
# install C lib with brew : brew install libxml2
# then get python bindings : ftp://xmlsoft.org/libxml2/python/
# 
# from lxml.html import soupparser
# import lxml
# 
# # make an element
# doc = soupparser.parse('test.html')
# 
# 
# from lxml.html import soupparser
# tree = soupparser.parse("./test.html")
# for outline in tree.findall("//outline"):
#   print outline.get('xmlUrl')

# http://stackoverflow.com/questions/8475377/python-xml-absolute-path

#from lxml.html import soupparser
from lxml import etree
import urllib2
import operator

# if XHTML then xml parser, elif html then html parser

# root = etree.HTML('''
# <html><head><title>Vous Etes Perdu ?</title></head><body><h1>Perdu sur l'Internet ?</h1><h2>Pas de panique, on va vous aider</h2><strong><pre>    * <----- vous &ecirc;tes ici</pre></strong></body></html>
# ''')

#url = "http://www.perdu.com/"
url = 'http://www.lacuisinehelene.com/2012/02/pita-with-hummus-veggies-and-feta.html'
# doc = etree.parse()
root = etree.HTML(urllib2.urlopen(url).read())
d = {}

def print_path_of_elems(elem, elem_path=""):
    for child in elem:
        if not child.getchildren():
            # leaf node with text => print
#            print "%s/%s, %s" % (elem_path, child.tag, child.text)
#            print "%s/%s" % (elem_path, child.tag)
			full_path = "%s/%s" % (elem_path, child.tag)
#			full_path_len = len(full_path.split('/'))
#			path_and_len = (full_path, full_path_len)
			if d.has_key(full_path):
				d[full_path] = d.get(full_path, 0) + 1
			else:
				d[full_path] = 1
			# d[(full_path_lst)] = len(full_path_lst)
			# print d
			
        else:
            # node with child elements => recurse
            print_path_of_elems(child, "%s/%s" % (elem_path, child.tag))

print_path_of_elems(root, root.tag)
sorted_d = sorted(d.iteritems(), key=operator.itemgetter(1), reverse=True)
#print type(sorted_d)
for each in sorted_d:
	print each

