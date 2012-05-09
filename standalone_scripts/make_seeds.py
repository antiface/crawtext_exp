#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# By Antoine Mazières -- http://ant1.cc/
# For CorText Project -- http://cortext.fr/
# CC-BY-CA
#
# This script query a Seeks server ($seeks_node) and return a list of seeds URL to crawl
# usage for debug : python ./make_seeds.py | tee log.txt && wc -l log.txt

import json
import urllib
import pprint
import sys
import os
import string

# tweak a textmate bug
reload(sys) 
sys.setdefaultencoding("utf-8")
#

# tweak a textmate bug
reload(sys) 
sys.setdefaultencoding("utf-8")
#

num_results = 1000
seeks_node = '67.23.28.136'
result = '%s' % urllib.urlopen('http://%s/search.php/search/txt/q=volcan?output=json&rpp=%d&expansion=%d' % ( seeks_node, num_results, num_results )).read()

result_utf8 = unicode(result, errors='ignore')

result_json = json.loads('%s' % result_utf8)

for each in result_json['snippets']:
	print each['cite']
