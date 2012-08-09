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
from pattern.web import *
from random import choice
import pprint
import re


reload(sys) 
sys.setdefaultencoding("utf-8")

root_url = 'https://api.datamarket.azure.com/Bing/Search/'
markets_list = ["ar-XA","bg-BG","cs-CZ","da-DK","de-AT","de-CH","de-DE","el-GR","en-AU","en-CA","en-GB","en-ID","en-IE","en-IN","en-MY","en-NZ","en-PH","en-SG","en-US","en-XA","en-ZA","es-AR","es-CL","es-ES","es-MX","es-US","es-XL","et-EE","fi-FI","fr-BE","fr-CA","fr-CH","fr-FR","he-IL","hr-HR","hu-HU","it-IT","ja-JP","ko-KR","lt-LT","lv-LV","nb-NO","nl-BE","nl-NL","pl-PL","pt-BR","pt-PT","ro-RO","ru-RU","sk-SK","sl-SL","sv-SE","th-TH","tr-TR","uk-UA","zh-CN","zh-HK","zh-TW"]
user_agents = [u'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1', u'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2', u'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0', u'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00', ]
unwanted_extensions = ['css','js','gif','GIF','jpeg','JPEG','jpg','JPG','pdf','PDF','ico','ICO','png','PNG','dtd','DTD']
urls_db = {}

def query_bing(query_words, password, nb_results=10, market="fr-FR", username=''):
	# Formatting username and password for HTTP headers 
	base64string = base64.encodestring('%s:%s' % (username,password) )
	
	# Formatting query	
	query_clean = query_words.replace(' ','%20')

	# Checking Market validity
	if market not in markets_list:
		print "The market you specified is not supported by Bing API"
		print "Markets List: " + str(markets_list)
		sys.exit(1)

	# Limiting the number of results (This limit can be overcome > TODO, check "next" in bing answer)
	if nb_results > 50:
		print "Results are limited to 50. Set to 50."
		nb_results = 50

	query_url = 'Web?Query=%27'+('%s' % query_clean)+'%27&$top='+str(nb_results)+'&$format=JSON&Market=%27'+market+'%27'
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

	results_json = json.loads(results_utf8)
	results = results_json['d']['results']
	
	# Logging results in Database
	# Making list of Urls
	
	# list_url = []
	# 
	# connection = Connection()
	# connection = Connection('localhost', 27017)
	# 
	# timestamp = ''
	# for each in time.localtime()[:]:
	# 	timestamp += str(each)
	# 
	# db = connection['crawbing']
	# collection_name = "%s%s" % (query_words.replace(' ',''), timestamp)
	# collection = db['%s' % collection_name]

	results_json = json.loads(results_utf8)
	results = results_json['d']['results']
	print type(results)
	print len(results)
	for each in results:
		urls_db[each['Url']] = {'inlink': set(), 'outlink': set(), 'parsed': 0}
		# list_url.append(each['Url'])
		# collection.insert(each)
	print urls_db
	return urls_db


#extract Date
#decruft
#xpath
# != inlink and insidelink

	
def crawl(urls_db, query, depth=10, crawl_round=0):
	while crawl_round <= depth:
		print "[LOG] Crawler's round: ", crawl_round
		for each in urls_db.keys():
			if urls_db[each]['parsed'] == 0:
				url = URL(each)
				if url.mimetype == "text/html":
					print each
					try:
						content = url.open().read()
						if re.search(query.replace(' ','.*'), content, re.INGORECASE):
							urls = find_urls(content, unique=True)
							urls_db[each]['parsed'] = 1
						else:
							for not_relevant_content in urls_db[each]['inlink']:
								urls_db[not_relevant_content]['outlink'].discard(each)
							del urls_db[each]
					except:
						print "[LOG] Error while parsing %s. Passing." % each
						urls_db[each]['parsed'] = 2
						urls = []
					for found_url in urls:
						if len(found_url.split('"')) > 1:				# Tweak Pattern bug on find_urls output format
							found_url = found_url.split('"')[0] 
						if len(found_url.split(');')) > 1:				# IDEM
							found_url = found_url.split(');')[0]
						if len(found_url.split('#')) > 1:				# Strip Anchors
							found_url = found_url.split('#')[0]
						if found_url.split('.')[-1] not in unwanted_extensions:
							urls_db[each]['outlink'].add(found_url)
							try:
								urls_db[found_url]['inlink'].add(each)
							except KeyError:
								urls_db[found_url] = {'inlink': set(), 'outlink': set(), 'parsed': 0}
								urls_db[found_url]['inlink'].add(each)
						
				else:													# Discard not html pages, and wipe them in inlink and outlink
					for point_to_not_html in urls_db[each]['inlink']:
						urls_db[point_to_not_html]['outlink'].discard(each)
					del urls_db[each]
		crawl_round += 1
		return crawl(urls_db, 'Algues Vertes', depth=depth, crawl_round=crawl_round )
	if crawl_round == depth:
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(urls_db)
		return urls_db	

			
#query_bing("Algues Vertes","HIDDEN", nb_results=2)

urls_db = {u'http://fr.wikipedia.org/wiki/Mar%C3%A9e_verte': {'outlink': set([]), 'parsed': 0, 'inlink': set([])}, u'http://fr.wikipedia.org/wiki/Algue_verte': {'outlink': set([]), 'parsed': 0, 'inlink': set([])}}


crawl(urls_db, 'Algues Vertes', depth=2)