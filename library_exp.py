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

def make_seeds(query,nb_results):
    try:
        os.mkdir('data/%s' % (query.replace(' ','_')))
    except:
        print "delete or rename the existing directory data/%s" % (query.replace(' ','_'))
        break
    seeds_file = open('data/%s/%s.txt' % ((query.replace(' ','_')),(query.replace(' ','_'))), 'w')
    seeks_node = '67.23.28.136'
    query_seeks = '%s' % urllib.urlopen('http://%s/search.php/search/txt/q=%s?output=json&rpp=%d&expansion=%d' % ( seeks_node, query.replace(' ','+'), nb_results, nb_results )).read()
    result_utf8 = unicode(query_seeks, errors='ignore')
    result_json = json.loads('%s' % result_utf8)
    for each in result_json['snippets']:
        seeds_file.write("%s\n" % (each["cite"]))
    seeds_file.close()

