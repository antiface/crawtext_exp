#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# By Antoine Mazières -- http://ant1.cc/
# For CorText Project -- http://cortext.fr/
# CC-BY-CA
#

import json
#import simplejson as json
import urllib
import pprint
import sys

## tweak a textmate bug
#reload(sys) 
#sys.setdefaultencoding("utf-8")
##

#Big Request
result = urllib.urlopen('http://67.23.28.136/search.php/search/txt/q=toto?output=json&rpp=400&expansion=100').read()
#type(result)
#Little Request
#result = urllib.urlopen('http://www.seeks-project.info/search.php/search/txt/toto?output=json').read()

#result_coded = unicode(result, errors='ignore')
#print result_coded
#print result_coded

kary = json.loads(result)

 
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(kary)
# 

for each in kary['snippets']:
	print each['cite']

