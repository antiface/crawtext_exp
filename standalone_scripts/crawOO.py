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
import threading

user_agents = [u'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1', u'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2', u'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0', u'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00', ]

unwanted_extensions = ['css','js','gif','GIF','jpeg','JPEG','jpg','JPG','pdf','PDF','ico','ICO','png','PNG','dtd','DTD']

allowed_mimetypes = ['text/html']

class Page:
	def __init__(self, uri):
		self.uri = uri
		self.outlinks = set()
		self.pattern = URL(self.uri)

	def check_mimetype(self):
		if extension(self.pattern.page) in unwanted_extensions:
			return False
		else:
			return bool(self.pattern.mimetype == 'text/html')

	def get_src(self):
		self.src = URL(self.uri).open(user_agent=choice(user_agents)).read()

	def is_relevant(self):
		return bool(re.search(query.replace(' ','.*'), self.src, re.IGNORECASE))

	def get_outlinks(self):
		for found_url in find_urls(self.src, unique=True):
			if '"' in found_url:				# Tweak Pattern bug on find_urls output format
				found_url = found_url.split('"')[0] 
			if ');' in found_url:				# IDEM
				found_url = found_url.split(');')[0]
			if '#' in found_url:				# Strip Anchors
				found_url = found_url.split('#')[0]
			self.outlinks.add(found_url)


def parse(url):
	u = Page(url)
	print u.uri
	# if u.check_mimetype() and u.get_src() and u.is_relevant() and u.get_outlinks():
	# 	print u.outlinks
	if not u.check_mimetype():
		print '[LOG]:: The page %s is not HTML and won\'t be parsed: Discarded.' %  u.uri
		return
	u.get_src()
	if not u.is_relevant():
		print '[LOG]:: The page %s doesn\'t seem relevant regarding the query: Discarded.' % u.uri
		return
	print '[LOG]:: The page %s is relevant.' % u.uri
	u.get_outlinks()
	print '%d parsed links: ' % len(u.outlinks)
	print u.outlinks

def crawl(seeds, query, depth=2):
	print '[LOG]:: Starting Crawler with Depth set to %d' % depth
	print '[LOG]:: Seeds are %s' % str(seeds)
	print '[LOG]:: Query is "%s"' % query
	for url in seeds:
		t = threading.Thread(None, parse, None, (url,))
		t.start()


seeds = ['http://fr.wikipedia.org/wiki/Mar%C3%A9e_verte', 'http://www.perdu.com/','http://ant1.cc/files/diss_br.pdf']
query = "Algues Vertes"

crawl(seeds, query)
