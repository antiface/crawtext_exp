#!/usr/bin/python
# -*- coding: utf-8 -*-

# by @mazieres

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

def make_seeds(query,path,nb_results=1,expansion=1,lang="fr"):
	seeks_file_name = "%s.seeks" % (query.replace(' ','_'))
	seeks_file = open('%s/%s' % (path,seeks_file_name), 'w')
	seeks_node = '67.23.28.136'
	query_seeks = '%s' % urllib.urlopen('http://%s/search.php/search/txt/q=%s?lang=%s&output=json&rpp=%d&expansion=%d' % ( seeks_node, query.replace(' ','+'), lang, nb_results, expansion )).read()
	result_utf8 = unicode(query_seeks, errors='ignore')
	result_json = json.loads('%s' % result_utf8)
	for each in result_json['snippets']:
		seeks_file.write("%s\n" % (each["cite"]))
	seeks_file.close()

