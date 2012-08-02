#!/usr/bin/python

import sys
import os
import urllib2
import base64
import json
import pymongo
from pymongo import Connection
import string
import time

reload(sys) 
sys.setdefaultencoding("utf-8")

username = ''
password = 'HIDDEN'

base64string = base64.encodestring('%s:%s' % (username,password) )

query_words = "Algues"

root_url = 'https://api.datamarket.azure.com/Bing/Search/'
query_url = 'Web?Query=%27Algues%27&$top=10&$format=JSON&Market=%27fr-FR%27'
full_url = root_url + query_url

query = urllib2.Request(full_url)
query.add_header("Authorization", "Basic %s" % base64string )

print "Query URL: ", query.get_full_url()
for each in query.header_items():
	print each

try:
	results_utf8 = unicode(urllib2.urlopen(query).read(), errors='ignore')
except IOError as e:
    if hasattr(e, 'reason'):
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    elif hasattr(e, 'code'):
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error message: ', e.msg
        print 'Header: ', e.hdrs
        print 'FP: ', e.fp


connection = Connection()
connection = Connection('localhost', 27017)

timestamp = ''
for each in time.localtime()[:]:
	timestamp += str(each)

db = connection['seeds_bing']
collection_name = "%s%s" % (query_words.replace(' ',''), timestamp)
collection = db['%s' % collection_name]

results_json = json.loads(results_utf8)
results = results_json['d']['results']
print type(results)
print len(results)
for each in results:
	print each
	collection.insert(each)
	print "\n"
