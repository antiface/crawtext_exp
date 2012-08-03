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

root_url = 'https://api.datamarket.azure.com/Bing/Search/'
markets_list = ["ar-XA","bg-BG","cs-CZ","da-DK","de-AT","de-CH","de-DE","el-GR","en-AU","en-CA","en-GB","en-ID","en-IE","en-IN","en-MY","en-NZ","en-PH","en-SG","en-US","en-XA","en-ZA","es-AR","es-CL","es-ES","es-MX","es-US","es-XL","et-EE","fi-FI","fr-BE","fr-CA","fr-CH","fr-FR","he-IL","hr-HR","hu-HU","it-IT","ja-JP","ko-KR","lt-LT","lv-LV","nb-NO","nl-BE","nl-NL","pl-PL","pt-BR","pt-PT","ro-RO","ru-RU","sk-SK","sl-SL","sv-SE","th-TH","tr-TR","uk-UA","zh-CN","zh-HK","zh-TW"]

def query_bing(query_words, password, nb_results=10, market="fr-FR", username=''):
	# Formatting username and password for HTTP headers 
	base64string = base64.encodestring('%s:%s' % (username,password) )
	
	# Formatting query	
	query_words = query_words.replace(' ','%20')

	# Checking Market validity
	if market not in markets_list:
		print "The market you specified is not supported by Bing API"
		print "Markets List: " + str(markets_list)
		sys.exit(1)

	# Limiting the number of results (This limit can be overcome > TODO, check "next" in bing answer)
	if nb_results > 50:
		print "Results are limite to 50. Set to 50."
		nb_results = 50

	query_url = 'Web?Query=%27'+('%s' % query_words.replace(' ','%20'))+'%27&$top='+str(nb_results)+'&$format=JSON&Market=%27'+market+'%27'
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

	seen_url = set()
	tosee_url = set()

	db = connection['crawbing']
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

