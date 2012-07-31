#!/usr/bin/python

import sys
import os
import urllib2
import pattern
#from pybing import Bing
import base64

# reload(sys) 
# sys.setdefaultencoding("utf-8")

# uri_api = "https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?$query=%27toto%27$top=50&$format=json"
# 
# print uri_api
# 
# urllib.urlopen(uri_api).read()

# bing = Bing('V70jWhb+WY2ykr9XyXSzXm8ubketalQVNBkAO+cIFTU=')
# 
# response = bing.search_web('python bing')
# 
# print response['SearchResponse']['Web']['Total']
# 
# results = response['SearchResponse']['Web']['Results']
# 
# for result in results[:3]:
# 	print repr(result['Title'])

username = ''
password = 'HIDDEN'
#base64string = base64.encode('%s:%s' % (username,password) )
query_url = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27Algues%27&$top=10&$market="fr-FR"'

query = urllib2.Request(query_url)
# query.add_header("Authorization", "Basic %s" % base64string )
# query.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1")
query.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
query.add_header("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.3")
query.add_header("Accept-Encoding", "gzip,deflate,sdch")
query.add_header("Accept-Language", "fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4")
query.add_header("Authorization", "Basic base64.HIDDEN")
query.add_header("Connection", "keep-alive")
query.add_header("Host", "api.datamarket.azure.com")
query.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11")


print "Query URL: ", query.get_full_url()
for each in query.header_items():
	print each

try:
	print urllib2.urlopen(query).read()
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
# 
# #########
# 
# # create a password manager
# password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
# 
# # Add the username and password.
# # If we knew the realm, we could use it instead of ``None``.
# top_level_url = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1"
# password_mgr.add_password(None, top_level_url, username, password)
# 
# handler = urllib2.HTTPBasicAuthHandler(password_mgr)
# 
# # create "opener" (OpenerDirector instance)
# opener = urllib2.build_opener(handler)
# 
# # # use the opener to fetch a URL
# # opener.open(a_url)
# 
# # Install the opener.
# # Now all calls to urllib2.urlopen use our opener.
# urllib2.install_opener(opener)
# 
# try:
# 	urllib2.urlopen('https://api.datamarket.azure.com/Bing/Search/Web?Query=%27Xbox%27&$top=10&$skip=20').read()
# except IOError as e:
#     if hasattr(e, 'reason'):
#         print 'We failed to reach a server.'
#         print 'Reason: ', e.reason
#     elif hasattr(e, 'code'):
#         print 'The server couldn\'t fulfill the request.'
#         print 'Error code: ', e.code
#         print 'Error message: ', e.msg
#         print 'Header: ', e.hdrs
#         print 'FP: ', e.fp
# 
# ########







#request = urllib2.Request("https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?$query=%27toto%27$top=50&$format=json")
# 
# base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
# request.add_header("Authorization", "Basic %s" % base64string)   
# result = urllib2.urlopen(request)
# result.read()

# # Create an OpenerDirector with support for Basic HTTP Authentication...
# auth_handler = urllib2.HTTPBasicAuthHandler()
# auth_handler.add_password(realm='None',
#                           uri='https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1',
#                           user='ant1',
#                           passwd='HIDDEN')
# opener = urllib2.build_opener(auth_handler)
# # ...and install it globally so it can be used with urlopen.
# urllib2.install_opener(opener)
# urllib2.urlopen('https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?$query=%27toto%27$top=50&$format=json').read()
