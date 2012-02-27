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


from lxml.html import soupparser
tree = soupparser.parse("./index.html")
for outline in tree.findall("//outline"):
  print outline.get('xmlUrl')