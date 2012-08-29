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
from decruft import Document
import operator
from lxml import etree
import copy

reload(sys) 
sys.setdefaultencoding("utf-8")

user_agents = [u'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1', u'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2', u'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0', u'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00', ]

unwanted_extensions = ['css','js','gif','GIF','jpeg','JPEG','jpg','JPG','pdf','PDF','ico','ICO','png','PNG','dtd','DTD']

allowed_mimetypes = ['text/html']

new_seeds = set()
next_seeds = set()

posts = {}

threads = []

class Content:
	def __init__(self, src):
		self.raw_src = src
		self.xml_src = etree.HTML(src)

	def get_content_xpath(self):
		d = {}
		self.xpath = ''
		def build_xpath(src_xml, src_xml_tag):
			for child in src_xml:
				if not child.getchildren() and child.text:
					full_path = "/%s/%s" % (src_xml_tag, child.tag)
					if d.has_key(full_path):
						d[full_path] += [len(child.text)]
					else:
						d[full_path] = [len(child.text)]
				else:
					build_xpath(child, "%s/%s" % (src_xml_tag, child.tag))
		build_xpath(self.xml_src, self.xml_src.tag)
		d_average = {x: sum(d[x]) for x in d}	#/len(d[x])
		d_sorted = sorted(d_average.iteritems(), key=operator.itemgetter(1), reverse=True)
		xpath_ranking = [x for x in d_sorted if not any(_ in x[0] for _ in ['style', 'script','built-in'])]
		for i in range(1):
			for path in self.xml_src.xpath(xpath_ranking[i][0]):
				try:
					self.xpath += path.text
				except:
					pass

	def get_content_decruft(self):
		self.decruft = Document(self.raw_src).summary()


class Page:
	def __init__(self, uri):
		self.uri = uri
		self.outlinks = set()
		self.inlinks = set()
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

	def select_content(self, method):
		c = Content(self.src)
		if 'decruft' in method:
			c.get_content_decruft()
			self.content_decruft = c.decruft
		if 'xpath' in method:
			c.get_content_xpath()
			self.content_xpath = c.xpath

	def build_post(self):
		self.post = {}
		self.post['url'] = self.uri
		self.post['src'] = self.src
		self.post['outlinks'] = self.outlinks
		self.post['inlinks'] = self.inlinks
		self.post['content'] = {}
		if self.content_xpath:
			self.post['content']['xpath'] = self.content_xpath
		if self.content_decruft:
			self.post['content']['decruft'] = self.content_decruft
		posts[self.uri] = self.post


def build_inlinks_clean_outlinks(posts):
	viewed_urls = posts.keys()
	posts_cp = copy.deepcopy(posts)
	for each in posts:
		for url in posts[each]['outlinks']:
			if url in viewed_urls:
				posts_cp[url]['inlinks'].add(each)
			else:
				posts_cp[each]['outlinks'].remove(url)
	posts.update(posts_cp)

def parse(url):
	u = Page(url)
	if not u.check_mimetype():
		print '[LOG]:: The page %s is not HTML and won\'t be parsed: Discarded.' %  u.uri
		return
	u.get_src()
	if not u.is_relevant():
		print '[LOG]:: The page %s doesn\'t seem relevant regarding the query: Discarded.' % u.uri
		return
	print '[LOG]:: The page %s is relevant.' % u.uri
	u.get_outlinks()
	global new_seeds
	new_seeds = {x for x in u.outlinks if x not in posts.keys()}
	global next_seeds
	next_seeds = next_seeds.union(new_seeds)
	print '%d parsed links: ' % len(u.outlinks)
	u.select_content(['decruft','xpath'])
	u.build_post()

def crawl(seeds, query, depth=1):
	print '[LOG]:: Starting Crawler with Depth set to %d' % depth
	print '[LOG]:: Seeds are %s' % str(seeds)
	print '[LOG]:: Query is "%s"' % query
	while depth >= 0:
		for url in seeds:
			t = threading.Thread(None, parse, None, (url,))
			t.start()
			threads.append(t)
		for thread in threads:
			thread.join()
		seeds = {x for x in next_seeds if x not in posts.keys()}
		next_seeds.clear()
		depth -= 1
		crawl(seeds, query, depth)

seeds = set(['http://fr.wikipedia.org/wiki/Mar%C3%A9e_verte', 'http://www.perdu.com/','http://ant1.cc/files/diss_br.pdf','http://www.actu-environnement.com/ae/news/plan_algues_vertes_bretagne_8105.php4'])
query = "Algues Vertes"

crawl(seeds, query)

build_inlinks_clean_outlinks(posts)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(posts)
