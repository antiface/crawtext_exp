#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

import os
import sys
import seachengine2
import warnings
import zipfile
import yaml
from library import *
from  pattern import web

# tweak textmate/python bug on utf8
reload(sys) 
sys.setdefaultencoding("utf-8")

def unzip_file_into_dir(file, dir):
	try:
		os.mkdir(dir, 0777)
	except:
		pass
	zfobj = zipfile.ZipFile(file)
	for name in zfobj.namelist():
		if name.endswith('/'):
			try:
				os.mkdir(os.path.join(dir, name))
			except:
				pass
		else:
			outfile = open(os.path.join(dir, name), 'wb')
			outfile.write(zfobj.read(name))
			outfile.close()

		
print "Option set: Never print matching warnings"
warnings.filterwarnings("ignore")

global pages
pages={}
global pattern_date_fr
# try:
# 	os.mkdir('data')
# except:
# 	pass

try:
	print "Trying to read parameters from commandline..."
	user_parameters=sys.argv[1]
except:
	print "Reading arguments from crawl_parameters.yml"
	user_parameters='crawl_parameters.yml'

parameters = yaml.load('\n'.join(open(user_parameters,'r').readlines()))
print 'Loaded parameters: ', parameters

try:
	path = parameters['path']
except:
	print 'invalid parameters file'
	path=parameters['corpus_file']
print 'Path: ', path

inlinks_min=int(parameters.get('inlinks_min',1))
print "Minimum number of inlinks (default is 1): ", inlinks_min

depth=int(parameters.get('depth',10))
print "Crawl depth (default is 10): ", depth

if parameters.has_key('query'):
	query=parameters.get('query')
	print "Query: ", query
else:
	sys.exit("You need to enter a query, otherwise...")

result_path=parameters.get('result_path','output')
print "Crawl output path (default is ./output/): ", result_path

max_pages_number=int(parameters.get('max_pages_number',10000))
if max_pages_number == 999999:
	pass
else:
	max_pages_number=min(max_pages_number,100000)
print "Maximum number of pages (default is 10000): ", max_pages_number


if path[-4:]=='.zip':
		print 'unzipping' + path + '...'
		corpus_out = '/'.join(path.split('/')[:-1]) + '/'+query
		print corpus_out
		unzip_file_into_dir(path,corpus_out)
		path=corpus_out
		print 'Path: ',path


dirList=os.listdir(path)
print 'List of Pages in path: ',dirList
for fname in dirList[:]:
	pagelist =os.path.join(path,fname)
	try:
		url=web.URL(pagelist)
		chaine=url.download(cached=False)
		new_urls = map(lambda x: url_uniformer(x.split('">')[0]),web.find_urls(chaine, unique=True))
		if 'Google Search' in pagelist:
			 new_urls = map(lambda x:x.split("&amp;")[0],new_urls)
		for new_url in new_urls[:]:
			print "Checking for forbidden URL..."
			if not check_forbidden((new_url,'')) and not new_url in pages:
				pages[new_url]=inlinks_min
	except:
		pass
print 'Pages init: ', len(pages)
print 'Pages: ', pages

print "Naming database..."
db_name=os.path.join(result_path,query+'_crawl.db')


try:	
	os.mkdir(result_path)
	os.remove(os.path.join(result_path,query+'_crawl.db'))
	print 'Deleted: ', result_path+query+'_crawl.db'
except:
	pass

crawler=seachengine2.crawler(db_name)
try:
  crawler.createindextables()
except:
  print "Tables already exist, good."

crawler.crawl(pages,query=query,inlinks=inlinks_min,depth=depth,max_pages_number=max_pages_number,citations_whole=0)
exportcrawl2resolu(db_name,query,result_path)