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


from lxml import etree


root = etree.HTML('''
<html><head><title>Vous Etes Perdu ?</title></head><body><h1>Perdu sur l'Internet ?</h1><h2>Pas de panique, on va vous aider</h2><strong><pre>    * <----- vous &ecirc;tes ici</pre></strong></body></html>
''')

def print_path_of_elems(elem, elem_path=""):
    for child in elem:
        if not child.getchildren():
            # leaf node with text => print
            print "%s/%s, %s" % (elem_path, child.tag, child.text)
        else:
            # node with child elements => recurse
            print_path_of_elems(child, "%s/%s" % (elem_path, child.tag))

print_path_of_elems(root, root.tag)