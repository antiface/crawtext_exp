from lxml import etree
import urllib2
import operator
import re
import sys
from decruft import Document

reload(sys) 
sys.setdefaultencoding("utf-8")

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
		print xpath_ranking
		for i in range(1):
			for path in self.xml_src.xpath(xpath_ranking[i][0]):
				self.xpath += path.text

	def get_content_decruft(self):
		self.decruft = Document(self.raw_src).summary()
		



