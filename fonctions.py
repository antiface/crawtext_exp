#!/usr/bin/env python
# -*- coding: utf_8 -*-
import os, sys
reload(sys) 
sys.setdefaultencoding("utf-8")
from sqlite3 import *
import os, sys
import shutil
#sys.path.append('..')
from path import *
from math import modf, floor
import codecs
#import unicodedata
import csv
import pickle
import re as r
import re
from operator import itemgetter
import pickle
import sqlite3
import math
from copy import deepcopy
############FONCTIONS DE FILTRAGE DE RESEAU#############

def extractNtop(dictionnaire,N=3,type='dict'):
	dictionnaire_top={}
	l=dictionnaire.items()
	l.sort(key=itemgetter(1),reverse=True)
	if type=='list':
		return map(lambda x: x[0],l[:N])
	else:
		for x in l[:N]:
			dictionnaire_top[x[0]] = x[1] 
		return dictionnaire_top





def extractabove_thres(distance_bip,distance_thres):
	dictionnaire_thres={}
	for cle,val in distance_bip.iteritems():
		if val>=float(distance_thres):
			dictionnaire_thres[cle]=val
	return dictionnaire_thres



def extract_top(results_y,top,result_pubdate,norm='No',rank=None):
	authorized_y={}
	results_y_top={}
	if norm=='Time dependent':
		dict_pubyear={}
		for year in result_pubdate.values():
			dict_pubyear[year] = dict_pubyear.get(year,0.)+1.
		for y,val in  results_y.iteritems():
			counter = {}
			results_y_top[y] = {}
			for cle,data in val.iteritems():
				for dat in unique(data):
					counter[dat] = counter.get(dat,0.) + 1./float(dict_pubyear[result_pubdate[cle]])
			l=counter.items()
			l.sort(key=itemgetter(1),reverse=True)
			#print y,l
			authorize=[]
			for x in  l[:top]:
				authorize.append(x[0])
			authorized_y[y]=authorize
			for cle,data in val.iteritems():
				for dat in data:
					if dat in authorize:
						if rank==None:
							results_y_top[y].setdefault(cle,[]).append(dat)
						else:
							dict_tuple = (dat,data[dat])
							#if not cle  in results_y_top[y]:
							#	results_y_top[y][cle]={}
							#results_y_top[y][cle][dat]=data[dat]
							results_y_top[y].setdefault(cle,[]).append(dict_tuple)
	else:
		for y,val in results_y.iteritems():
			counter = {}
			results_y_top[y] = {}
			#when selecting the weight of each item, we count only once the occurrences of an item within the same notice
			for cle,data in val.iteritems():
				for dat in unique(data):
					counter[dat] = counter.get(dat,0) + 1
			l=counter.items()
			l.sort(key=itemgetter(1),reverse=True)
			#print y,l
			authorize=[]
			for x in  l[:top]:
				authorize.append(x[0])
			authorized_y[y]=authorize
			for cle,data in val.iteritems():
				for dat in data:
					if dat in authorize:
						if rank==None:
							results_y_top[y].setdefault(cle,[]).append(dat)
						else:
							dict_tuple = (dat,data[dat])
							results_y_top[y].setdefault(cle,[]).append(dict_tuple)
	return results_y_top,authorized_y



def convert2edgelist(dictionnaire):
	dictionnaire_edge={}
	for x,y in dictionnaire.iteritems():
		if not x[0] in  dictionnaire_edge:
			dictionnaire_edge[x[0]]={}
		dictionnaire_edge[x[0]][x[1]] = y
	return dictionnaire_edge

def extractNnearest(dictionnaire,N):
	dictionnaire_top={}
	dictionnaire_edge=convert2edgelist(dictionnaire)
	for x,y in dictionnaire_edge.iteritems():
		l=y.items()
		l.sort(key=itemgetter(1),reverse=True)
		for voisin in l[:N]:
			dictionnaire_top[(x,voisin[0])] = voisin[1]
	return dictionnaire_top

def removenodes(G,isolated):
	G_only_degpos=deepcopy(G)
	for x in G.nodes():
		if x in isolated:
			try:
				G_only_degpos.remove_node(x)
			except:
				pass
	for u,v in G.edges():
		if u in isolated or v in isolated:
			try:
				G_only_degpos.remove_edge(*(u,v))
			except:
				pass
	return G_only_degpos
	
def onlydegpos(G):
	G_only_degpos=deepcopy(G)
	node_degree_positive=[]
	for x,y in G.edges():
		if not x in node_degree_positive:
			node_degree_positive.append(x)
		if not y in node_degree_positive:
			node_degree_positive.append(y)
	for x in G.nodes():
		if not x in node_degree_positive:
			G_only_degpos.remove_node(x)
			print 'node ',x,' removed' 
	return G_only_degpos


def onlycommgraph(G,communitiesnodes):
	G_only_degpos=deepcopy(G)
	node_degree_positive=[]
	for x in G.nodes():
		if not x in communitiesnodes:
			G_only_degpos.remove_node(x)
	return G_only_degpos








class NLPlib:
	
	lexHash = {}
	
	def __init__(self):
		if(len(self.lexHash) == 0):
			try:
				print "     [unpickle the dictionary]"
				upkl = open('pickledlexicon', 'r')
				self.lexHash = pickle.load(upkl)
				upkl.close()
				print "     [Initialized lexHash from pickled data.]"
		
#				print "printing unpickled dictionary"
#				i = 0
#				for k,v in self.lexHash.iteritems():
#					if i == 100:
#						break
#					print k, ":", v
#					i = i+1
			
			except Exception, inst:
				print type(inst)
				print inst.args
	#finish - populatehash

	#start  - DEF: tokenize
	def tokenize(self,s):
		v = []
		reg = re.compile('(\S+)\s')
		m = reg.findall(s);
		
		#print m
		for m2 in m:
#			print m2
			if len(m2) > 0:
				if m2.endswith(";") or m2.endswith(",") or m2.endswith("?") or m2.endswith(")") or m2.endswith(":") or m2.endswith("."):
					v.append(m2[0:-1])
#					print "adding0: ",m2[0:-1]
				else:
					v.append(m2)
#					print "adding1: ",m2
#		print "\t",v
		return v
	#finish - DEF: tokenize

	#start  - DEF: tag
	def tag(self,words):
		ret = []
		#begin tagging
		for i in range(len(words)):
			ret.append("NN")		#the default entry
#			print "hash_key:",words[i]

			if self.lexHash.has_key(words[i]):
				ret[i] = self.lexHash[words[i]]
			else:
				if self.lexHash.has_key(words[i].lower()):
					ret[i] = self.lexHash[words[i].lower()]
		
		#apply transformational rules
		for i in range(len(words)):
			#rule 1 : DT, {VBD | VBP} --> DT, NN
			if i > 0 and ret[i-1] == "DT":
				if ret[i] == "VBD" or ret[i] == "VBP" or ret[i] == "VB":
					ret[i] = "NN"
					
			#rule 2: convert a noun to a number (CD) if "." appears in the word
			if ret[i].startswith("N"):
				if words[i].find(".") > -1:
					ret[i] = "CD"
			
			# rule 3: convert a noun to a past participle if ((string)words[i]) ends with "ed"
			if ret[i].startswith("N") and words[i].endswith("ed"):
				ret[i] = "VBN"

			# rule 4: convert any type to adverb if it ends in "ly"
			if words[i].endswith("ly"):
				ret[i] = "RB"
				
			# rule 5: convert a common noun (NN or NNS) to a adjective if it ends with "al"
			if ret[i].startswith("NN") and words[i].endswith("al"):
				ret[i] = "JJ"
				
			# rule 6: convert a noun to a verb if the preceeding work is "would"
			if i > 0 and ret[i].startswith("NN") and words[i - 1].lower() == "would":
				ret[i] = "VB"
			
			# rule 7: if a word has been categorized as a common noun and it ends with "s",
			# then set its type to plural common noun (NNS)
			if ret[i] == "NN" and words[i].endswith("s"):
				ret[i] = "NNS"
			
			# rule 8: convert a common noun to a present prticiple verb (i.e., a gerand)
			if ret[i].startswith("NN") and words[i].endswith("ing"):
				ret[i] = "VBG"
				
		return ret
	#finish - DEF: tag


#auxiliary functions
def sub_corpus(corpus):		
	corpus_seuil={}
	for x,y in corpus.iteritems():
		if int(x)<100:
			if int(x)>8:
				corpus_seuil[x]=y
	return corpus_seuil



def dumpingin(data,datastr,resultpath=''):
	try:
		os.mkdir(os.path.join(resultpath,'pkl'))
		print '/pkl/'  + ' créé '
	except:
		pass
	output = open(os.path.join(resultpath,'pkl/'+datastr+'.pkl'), 'wb')
	pickle.dump(data, output)
	output.close()


def dumpingout(datastr,resultpath=''):
	pkl_file = open(os.path.join(resultpath,'pkl/'+datastr+'.pkl'), 'rb')
	data = pickle.load(pkl_file)
	return data

def tag_extract(chunk):
	return [x[1] for x in chunk],[x[0] for x in chunk]

def tag_exclude(chunk):
	return [x[0] for x in chunk]

		
def strip_tag(nlemme):
	return ' '.join(tag_exclude(nlemme))

def make_dict_doublet_from_dict_dict(biparti_dict):
	biparti_doublet={}	
	for x,vois_x in biparti_dict.iteritems():
		for vois,val in vois_x.iteritems():
			biparti_doublet[x,vois]=val
	return biparti_doublet

def make_dict_dict_from_dict_doublet(biparti_doublet):
	biparti_dict={}	
	for (x1,x2),val in biparti_doublet.iteritems():
		if not x1 in biparti_dict:
			biparti_dict[x1]={}
		biparti_dict[x1][x2]=val
	return biparti_dict

def make_result_norank(results):#turns 'GEP-wos_12607': [(u'Luo L_1999_NAT MED', {15: [0]})] into 'GEP-wos_9849': [u'SCHENA M_1995_SCIENCE']
	resultsbis={}
	for x,list in results.iteritems():
		resultsbis[x] = map(lambda x : x[0],list)
	return resultsbis
		
def merge(d1, d2, merge=lambda x,y:y):
    """
    Merges two dictionaries, non-destructively, combining 
    values on duplicate keys as defined by the optional merge
    function.  The default behavior replaces the values in d1
    with corresponding values in d2.  (There is no other generally
    applicable merge strategy, but often you'll have homogeneous 
    types in your dicts, so specifying a merge technique can be 
    valuable.)

    Examples:

    >>> d1
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1)
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1, lambda x,y: x+y)
    {'a': 2, 'c': 6, 'b': 4}

    """
    result = dict(d1)
    for k,v in d2.iteritems():
        if k in result:
            result[k] = merge(result[k], v)
        else:
            result[k] = v
    return result

def normalize(dict):
	normal=float(sum(dict.values()))
	dict_norm={}
	for x,y in dict.iteritems():
		dict_norm[x] = float(y) / normal
	return dict_norm
	
def merge_support(d1, d2, merge=lambda x,y:y):
    """
    Merges two dictionaries, non-destructively, combining 
    values on duplicate keys as defined by the optional merge
    function.  The default behavior replaces the values in d1
    with corresponding values in d2.  (There is no other generally
    applicable merge strategy, but often you'll have homogeneous 
    types in your dicts, so specifying a merge technique can be 
    valuable.)

    Examples:

    >>> d1
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1)
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1, lambda x,y: x+y)
    {'a': 2, 'c': 6, 'b': 4}

    """
    result = dict(d1)
    for k,v in d1.iteritems():
        if k in d2:
            result[k] = merge(d2[k], v)
        else:
            result[k] = 0.
    return result

def top_dict(dict,n=1):
	l=dict.items()
	l.sort(key=itemgetter(1),reverse=True)
	dict_n= {}
	for couple in l[:n]:
		dict_n[couple[0]]=couple[1]
	return dict_n

def filter_dict(dict,thres=2):
	dict_thres= {}
	for x,y in dict.iteritems():
		if y>=thres:
			dict_thres[x]=y
	return dict_thres


def top(dict,n=1):
	l=dict.items()
	l.sort(key=itemgetter(1),reverse=True)
	return l[:n]

def excelize(floating):
	try:
		return str(floating).replace('.',',')
	except:
		if floating==None:
			return ''
	
def create_bdd(name_database):
	print name_database, ' created '
	conn = connect(name_database)
	conn.text_factory = OptimizedUnicode
	curs = conn.cursor()
	return conn, curs

def tolist(ltuple):
    totlist=[]
    for line in ltuple:
        totlist.append(list(line))
    return totlist

def convert_ligne(string):
	newstring= string.replace('$ligne$','\n')
	return newstring
		
def lire_parametre_ini(fichier_name_ini):
	file_in = open(fichier_name_ini,'r')
	lignes = file_in.readlines()
	dico_tag={}
	for ligne in lignes:
		if ligne[0] != '#':
			line = ligne[:-1]
			line_v=line.split('\t')
			if len(line_v)>1:
				if len(line_v)>4:
					dico_tag[line_v[0]]=(line_v[1],list(map(convert_ligne,line_v[2:])))
				dico_tag[line_v[0]]=(line_v[1],list(map(convert_ligne,line_v[2:])))
	return dico_tag



def minimal_chain(chaine):
	if type(chaine)==list:
		chaine_v=chaine
	else:
		chaine_v=chaine.split('|&|')
	#print 'chaine_v',chaine_v
	chaine_v_l=[]
	for i,x in enumerate(chaine_v[:]):
		#print x, 'evalue' 
		clause=0
		x=x
		for y in chaine_v_l[:]:
			y=y
			#print '*compared to=',y
			if x in y and x!=y:
				chaine_v_l.remove(y)
				#print '**on elimine',y
			elif y in x and x!=y:
				#print '**on a deja y:',y,'qui inclut,',x
				clause='out'
				break
			elif x==y:
				#print '**du deja vu:',x
				clause='out'
				break
		if not clause=='out':
			#print '**nouvelle chaine=',x
			chaine_v_l.append(x)
	if type(chaine)==list:
		return(unique(chaine_v_l))
	else:
		return '|&|'.join(unique(chaine_v_l))


def inside(x,y):
	tot=0
	if ' '.join(x) in ' '.join(y):
		for elemx in x:
			if elemx in y:
				tot+=1
		if tot==len(x):
			return True
		else:
			return False
	else:
		return False
		
def deboite(chaine):
	if type(chaine)==list:
		chaine_v=chaine
	else:
		chaine_v=chaine.split('|&|')
	chaine_v_l=[]
	
	for i,x in enumerate(chaine_v[:]):
		clause=0
		x=x.split()
		for y in chaine_v_l[:]:
			y=y.split()
			if inside(x,y):
				chaine_v_l.remove(' '.join(y))
				chaine_v_l.append(' '.join(x))
				clause=1
			if inside(y,x):
				clause=1
				break
		if clause==0:
			chaine_v_l.append(' '.join(x))
	if type(chaine)==list:
 		return unique(chaine_v_l)
	else:
		return '|&|'.join(unique(chaine_v_l))



def make_dir(dir):
	try:
		os.mkdir (dir)
	except:
		pass	


def quantile(x, q,  qtype = 7, issorted = False):
	
    """
    Args:
       x - input data
       q - quantile
       qtype - algorithm
       issorted- True if x already sorted.

    Compute quantiles from input array x given q.For median,
    specify q=0.5.

    References:
       http://reference.wolfram.com/mathematica/ref/Quantile.html
       http://wiki.r-project.org/rwiki/doku.php?id=rdoc:stats:quantile

    Author:
	Ernesto P.Adorio Ph.D.
	UP Extension Program in Pampanga, Clark Field.
    """

    if not issorted:
        y = sorted(x)
    else:
        y = x
    if not (1 <= qtype <= 9): 
       return None  # error!

    # Parameters for the Hyndman and Fan algorithm
    abcd = [(0,   0, 1, 0), # inverse empirical distrib.function., R type 1
            (0.5, 0, 1, 0), # similar to type 1, averaged, R type 2
            (0.5, 0, 0, 0), # nearest order statistic,(SAS) R type 3

            (0,   0, 0, 1), # California linear interpolation, R type 4
            (0.5, 0, 0, 1), # hydrologists method, R type 5
            (0,   1, 0, 1), # mean-based estimate(Weibull method), (SPSS,Minitab), type 6 
            (1,  -1, 0, 1), # mode-based method,(S, S-Plus), R type 7
            (1.0/3, 1.0/3, 0, 1), # median-unbiased ,  R type 8
            (3/8.0, 0.25, 0, 1)   # normal-unbiased, R type 9.
           ]

    a, b, c, d = abcd[qtype-1]
    n = len(x)
    g, j = modf( a + (n+b) * q -1)
    if j < 0:
        return y[0]
    elif j >= n:           
        return y[n-1]   # oct. 8, 2010 y[n]???!! uncaught  off by 1 error!!!

    j = int(floor(j))
    if g ==  0:
       return y[j]
    else:
       return y[j] + (y[j+1]- y[j])* (c + d * g)    


	
def load_parameters(user_parameters):	
	import yaml
	try:
		user_parameters=sys.argv[1]
		print 'Try to load ',user_parameters
		parameters_user = yaml.load('\n'.join(open(user_parameters,'r').readlines()))				
	except:
		try:
			if "iscpif" in os.getcwd():
				user_parameters='../parameters/param_ex_isc.yml'
			elif 'louiseduloquin' in os.getcwd():
				user_parameters='../parameters/param_ex_imac.yml'
			else:
				user_parameters='../parameters/param_ex.yml'
			print 'failed,\n try to load ', user_parameters
			parameters_user = yaml.load('\n'.join(open(user_parameters,'r').readlines()))		
		except:
			print 'failed,\n try to load ',sys.argv[0].split('/')[-2] + '.yml'
			user_parameters=sys.argv[0].split('/')[-2] + '.yml'
			parameters_user = yaml.load('\n'.join(open(user_parameters,'r').readlines()))				
			
	return parameters_user



def get_nodes_edges(G,pos=None):#à partir de G, on récupère l'ensemble des infos reindexées
	index,retroindex={},{}#dictionnaire index->label noeud
	nodes={}
	edges={}
	for node_count,rn in enumerate(G.nodes()):
		index[node_count+1]=rn
		retroindex[rn]=node_count+1
	for node_count,rn in enumerate(G.nodes()):
		attributs_i={} 
		attributs_i['label'] = rn
		for key,val in G.node[rn].iteritems():
			attributs_i[key]=val
		if len(pos.keys())>0:
			attributs_i['x']=float(pos[rn][0])
			attributs_i['y']=float(pos[rn][1])
		nodes[node_count+1] = attributs_i
	edge_count=0
	edges_list=[]
	for node in G.nodes():
		for y,edge_att in G[node].iteritems():
			edge_count+=1
			edge_attribute_i={}
			edge_attribute_i['source']=retroindex[node]
			edge_attribute_i['dest']=retroindex[y]
			try:
				edge_attribute_i['level']=G.node[node]['level']
			except:
				pass
			for key,val in edge_att.iteritems():
				edge_attribute_i[key]=val			
			edges[edge_count]=edge_attribute_i	
			try:
				edges_list.append(str(edge_attribute_i['source']) + ' ' + str(edge_attribute_i['dest'])+ ' '+str(edge_attribute_i['weight'])) 
			except:
				edges_list.append(str(edge_attribute_i['source']) + ' ' + str(edge_attribute_i['dest']))
	return	nodes,edges,edges_list,index


def get_edges_list(G):#à partir de G, on récupère l'ensemble des infos reindexées
	index,retroindex={},{}#dictionnaire index->label noeud
	edges={}
	for node_count,rn in enumerate(G.nodes()):
		index[node_count+1]=rn
		retroindex[rn]=node_count+1
	# for node_count,rn in enumerate(G.nodes()):
	# 	attributs_i={} 
	# 	attributs_i['label'] = rn
	# 	for key,val in G.node[rn].iteritems():
	# 		attributs_i[key]=val
	# 	if len(pos.keys())>0:
	# 		attributs_i['x']=float(pos[rn][0])
	# 		attributs_i['y']=float(pos[rn][1])
	# 	nodes[node_count+1] = attributs_i
	edge_count=0
	edges_list=[]
	for node in G.nodes():
		for y,edge_att in G[node].iteritems():
			edge_count+=1
			edge_attribute_i={}
			edge_attribute_i['source']=retroindex[node]
			edge_attribute_i['dest']=retroindex[y]
			for key,val in edge_att.iteritems():
				edge_attribute_i[key]=val			
			edges[edge_count]=edge_attribute_i	
			try:
				edges_list.append(str(edge_attribute_i['source']) + ' ' + str(edge_attribute_i['dest'])+ ' '+str(edge_attribute_i['weight'])) 
			except:
				edges_list.append(str(edge_attribute_i['source']) + ' ' + str(edge_attribute_i['dest']))
	return	edges_list,index


	
#def export_networkG(G,pos2d,type_export,result_path,name):
def export_networkG(graph,type_export,result_path,name=''):
	import simplejson as json
	y=graph['meta']['period']
	nodes=graph['nodes']
	edges=graph['edges']
	try:
		os.mkdir(os.path.join(result_path,'carto'))
	except:
		pass
	try:
		os.mkdir(os.path.join(os.path.join(result_path,'carto'),'json'))
	except:
		pass
	result_path=os.path.join(os.path.join(result_path,'carto'),'json')
	result=json.dumps(graph,indent=4)
	file_name=os.path.join(result_path,'hnetwork-'+y+name+'.json')
	print '++++++++++++++++json:  '+file_name + ' written to disk '
	f = open(file_name,"w+")
	f.write(result)
	#export gexf
	file_name=os.path.join(result_path,'hnetwork-'+y+name+'.gexf')
	print file_name
	exportgexf(graph,file_name,name=name)




# self.graph_obj.addNodeAttribute(title, default, type, mode, force_id=id)
# self.graph_obj.addEdgeAttribute(title, default, type, mode, force_id=id)



#addNode(self,id,label,start="",end="",pid="",r="",g="",b="") :
#addEdge(self,id,source,target,weight="",start="",end="",label="") :
#addNodeAttribute(self,title,defaultValue,type="integer",mode="static", force_id="") :
#EXAMPLES/

# graph=gexf.addGraph("undirected","static",year)
# idAttType=graph.addNodeAttribute("type","professer","string")
# idAttInstAgreg=graph.addNodeAttribute("agregation","N/A","string")
# labels_agregation=("champs","groupe","institution")
# idAttInstCat1=graph.addNodeAttribute("champs","professors","string")
# idAttDiscipline=graph.addNodeAttribute("discipline","N/A","string")
# idAttWeak=graph.addEdgeAttribute("weak","false","boolean")


# n=graph.addNode("inst_"+str(id),name)
# n.addAttribute(idAttType,"institution")
# n.addAttribute(idAttInstAgreg,labels_agregation[int(depth)])

#e=graph.addEdge(edgesKeygen.next(),"prof_"+str(id),"inst_"+str(extraID))
#e.setColor("255","0","0");
#e.addAttribute(idAttWeak,"true")


# <viz:color r="239" g="173" b="66" a="0.6"/>
# <viz:position x="15.783598" y="40.109245" z="0.0"/>
# <viz:size value="2.0375757"/>
# <viz:shape value="disc"/>


#string ”disc” |string ”square” | string ”triangle” | string ”diamond” | string ”image”


# if export_gexf :
# 	file=open("outdata/profiep_profToinst_"+year+".gexf","w+")
# 	gexf.write(file)

def get_all_keys(dict_dict):
	node_attributes={}
	for node,node_info in dict_dict.iteritems():
		for att in node_info:
			if not att in node_attributes:
				node_attributes[att]='string'
	return node_attributes


def exportgexf(net,file_name,name=''):
	#from gexf import Gexf,GexfImport
	from gexfbis import Gexf,GexfImport
	
	#gexf_file=gexf.Gexf("Paul Girard medialab Sciences Po","IEP professers linked by common institutions "+name)
	#graph=gexf_file.addGraph("undirected","static",name)
	
	
	#from gexf import Gexf,GexfImport

	# test helloworld.gexf
	nodes=net['nodes']
	edges=net['edges']
	#rename attribute name to avoid twice the same name between nodes and links
	for edge,edge_info in edges.iteritems():
		edege_info_new = {}
		for att,att_value in edge_info.iteritems():
			edege_info_new[att+'_edge'] = att_value
		edges[edge]=edege_info_new
	for node,node_info in nodes.iteritems():
		if 'shape' in node_info:
			if node_info['shape'] == 'o':
				node_info['shape']='disc'
			if node_info['shape'] == 's':
				node_info['shape']='square'
			if node_info['shape'] == 'd':
				node_info['shape']='diamond'
				
		nodes[node]=node_info
		
	
	node_attributes=get_all_keys(nodes)
	edge_attributes=get_all_keys(edges)
	#print edge_attributes
	for att in node_attributes:
		if att=='weight':
			node_attributes[att] = 'float'
		#if att=='community':
		#	node_attributes[att] = 'float'
		if att=='x':
			node_attributes[att] = 'float'
		if att=='y':
			node_attributes[att] = 'float'

	for att in edge_attributes:
		if att=='weight_edge':
			edge_attributes[att] = 'float'

	
	#{'category': 'ISIterms & classe_hab3', 'weight': 410050.0, 'level': 'high', 'community': 2, 'label': '3 & national', 'shape': 'o', 'y': 0.79811585269087315, 'x': 0.82098563183619633}
	#1 {'dest': 1, 'source': 1, 'weight': 0.0075719476644008007, 'level': 'high'}
	gexf = Gexf("CorText",name)
	graph=gexf.addGraph("undirected","static",name)

	for att,type_att in node_attributes.iteritems():
		vars()[att]=graph.addNodeAttribute(att,"",type_att)
		
		
	for att,type_att in edge_attributes.iteritems():
		vars()[att]=graph.addEdgeAttribute(att,"",type_att)
	
	for node,node_info in nodes.iteritems():
		#print node,node_info
		if 'x' in node_attributes and  'y' in node_attributes :
			#print node_info['shape']
			n=graph.addNode(node,unicode(node_info['label']),x=str(float(node_info['x'])*1000.),y=str(float(node_info['y'])*1000.),z=str(float(node_info.get('z',0.))*1000.),shape=node_info['shape'])
		else:
			n=graph.addNode(node,unicode(node_info['label']),r="239" ,g="173" ,b="66",shape=node_info['shape'])
		for att,att_value in node_info.iteritems():
			#print att,att_value,'ici'
			if node_attributes[att]=='string':
				n.addAttribute(vars()[att],unicode(att_value))
			else:
				n.addAttribute(vars()[att],str(att_value))
		
	for edge,edge_info in edges.iteritems():
		#print edge,edge_info['source_edge'],edge_info['dest_edge']
		e=graph.addEdge(edge,edge_info['source_edge'],edge_info['dest_edge'],weight=str(edge_info.get('weight_edge',1.)))
		for att,att_value in edge_info.iteritems():
			if edge_attributes[att]=='string':
				#print att,att_value
				#print edge_attributes
				e.addAttribute(vars()[att],unicode(att_value))
			else:
				e.addAttribute(vars()[att],str(att_value))
				
		
		
	#graph.addNode("0","hello")
	#graph.addNode("1","World")
	#graph.addEdge("0","0","1")
	#print file_name
	output_file=open(file_name,"w")
	gexf.write(output_file)
	
	

def export_network(n,c,type_export,result_path):
	import simplejson as json
	
	print type_export
	print result_path
	print os.path.join(result_path,'collaboration_network')
	try:
		shutil.copytree(os.path.join('./library','collaboration_network_template'),os.path.join(result_path,'collaboration_network'))
	except:
		pass
		
	if 'json' in type_export:
		#shutil.copy(os.path.join('./library','collaboration_network_template','network_html'),os.path.join(result_path,corpus_name,'collaboration_network'))
		try:
			os.rename(os.path.join(result_path,'collaboration_network','network_html'),os.path.join(result_path,'collaboration_network','index_protovis.html'))
			json_file=os.path.join(result_path,'collaboration_network','network.js')
			print 'json_file'
			print json_file
			f = open(json_file,'w')
			f.write('// This file contains the weighted network"\n var network = {\n  nodes:[ \n')
			for rn in n:
				f.write('    {nodeName:"'+ str(rn[1]) + '", group:1}, \n')
			f.write('  ], \n        links:[ \n')
			for row in c:
				f.write('    {source:'+ str(int(row[0])-1) + ', target:' + str(int(row [1])-1) + ', value:' + str(row[2]) + '},\n')
			f.write('  ]\n};')     
			f.close()
			print '++++++++++++++++json: fichier '+ json_file + ' ecrit '
		except:
			print '++++++++++++++++json: fichier '+ ' deja ecrit '
	if 'gexf' in type_export:
		
		try:
			os.rename(os.path.join(result_path,'collaboration_network','sigma_layout_html'),os.path.join(result_path,'collaboration_network','index_sigma.html'))
		except:
			pass
		print os.path.join(path_library,'gexf_template_collaboration.xml')
		import gexf
		
		gexf_file=os.path.join(result_path,'collaboration_network','collaboration.gexf')
		nodes,edges,weight={},{},{}
		for node in n:
			nodes[node[0]]=node[1]
			weight[node[0]]=node[2]
		for edge in c:
			edges[(edge[0],edge[1])]=edge[2]
		gexf.gexf_builder(nodes,edges,weight,gexf_file,'collaboration')
		
def slug(texte,limit=5):
	compt,wait=0,0
	slugged_text=''
	for t in texte:
		#print 't',t
		if t==' ' or t== '-' or t=='\n':
			slugged_text=slugged_text+t
			compt=0
			wait=0
		else:
			if wait==0:
				compt+=1
				if compt<=limit:
					slugged_text=slugged_text+t
				else:
					compt=0
					wait=1
	return slugged_text
				
def expand(pos2d,dim=2,factor=1):
	xmin=100000
	xmax = -100000
	ymin=100000
	ymax = -100000	
	for x,pos in pos2d.iteritems():
		xmin=min(pos[0],xmin)
		if dim>1:
			ymin=min(pos[1],ymin)
			ymax=max(pos[1],ymax)
		xmax=max(pos[0],xmax)

	for x,pos in pos2d.iteritems():
		pos2d[x][0]=(pos[0]-xmin) / (xmax-xmin)/float(factor)
		if dim>1:
			pos2d[x][1]=(pos[1]-ymin) / (ymax-ymin) 
	return pos2d

def compute_mean_position(communities,pos2d,pos_high,community_label):
	for i,comm in enumerate(communities):
		pos_h=pos_high[community_label[i]]
		pos_h[0]=0.
		pos_h[1]=0.
		for noeud in comm:
			pos_h[0] = pos2d[noeud][0] + pos_h[0]
			pos_h[1] = pos2d[noeud][1] + pos_h[1]
		pos_h[0] = pos_h[0] / float(len(comm))
		pos_h[1] = pos_h[1] / float(len(comm))
		pos_high[community_label[i]]=pos_h
	return pos_high


def unique(list):
	listunique=[]
	for x in list:
		if x not in listunique:
			listunique.append(x)
	return listunique
	

def sym_no_doublon(dictionnaire_cooccurrences):
	dictionnaire_cooccurrences_propre={}
	for x,y in dictionnaire_cooccurrences.iteritems():
		if x[0] != x[1]:
			dictionnaire_cooccurrences_propre[x]=y
			dictionnaire_cooccurrences_propre[(x[1],x[0])]=y
	return dictionnaire_cooccurrences_propre

def voisins(dictionnaire_cooccurrences):
	dictionnaire_voisins={}
	for x,y in dictionnaire_cooccurrences.iteritems():
		dictionnaire_voisins_x=dictionnaire_voisins.get(x[0],{})
		dictionnaire_voisins_x[x[1]]=dictionnaire_voisins_x.get(x[1],0)+y
		dictionnaire_voisins[x[0]]=	dictionnaire_voisins_x
	return dictionnaire_voisins


def distance_min(parserank1,parserank2):
	mindist=10000
	output=[]
	for place1 in parserank1:
		for place2 in parserank2:
			if place1==None or place2==None:
				return 1
			else:
				mindist= math.fabs(place2-place1)
				if mindist==0:
					return 1.
	if mindist<=5:
		return math.pow(mindist,-1)
	else:
		return False



def distance_places(places1,places2):
	proximity=0
	for rank1,parserankl1 in places1.iteritems():
		for parserank1 in parserankl1:
			for rank2,parserankl2 in places2.iteritems():
				for parserank2 in parserankl2:				
					if rank1==0 or rank2==0:
						proximity+= 1.
					else:
						#proximity = distance_min(parserank1,parserank2)
						try:
							diff=math.fabs(parserank1-parserank2)
							if diff==0:
								proximity+= 1.
							else:
								proximity+=math.pow(diff,-1)
						except:#one of the parseranks is None:
							proximity+=1
	#print places1,places2,proximity
	return proximity

def add_links_clique(biparti,clique1,clique2,type_biparti,rank=None):
	#print 'clique1,clique2',clique1,clique2
	for x1 in clique1:
		for x2 in clique2:		
			if rank==None:
				biparti[(x1,x2)] = biparti.get((x1,x2),0) + 1
				if not type_biparti==True:
					biparti[(x2,x1)] = biparti.get((x2,x1),0) + 1
			else:
				places1=x1[1]
				places2=x2[1]
				proximity = distance_places(places1,places2) 
				#print places1,places2,proximity
				#print proximity
				if not proximity==False:#proximity can be false
					biparti[(x1[0],x2[0])] = biparti.get((x1[0],x2[0]),0) + proximity
					if not type_biparti==True:
						biparti[(x2[0],x1[0])] = biparti.get((x2[0],x1[0]),0) + proximity
	return biparti

def distance(dictionnaire_cooccurrences,type_distance='chi2',type_biparti=False):
	#print 'dictionnaire_cooccurrences',dictionnaire_cooccurrences
	if type_distance in ["chi2","chi2_complete",'chi2_squared','mutual information','chi2_yates','PEM','cramer','chi2_complete','chi2_complete_yates','distributional']:
		dictionnaire_cooccurrences = sym_no_doublon(dictionnaire_cooccurrences)
	#print 'dictionnaire_cooccurrences',dictionnaire_cooccurrences
	#dictionnaire_cooccurrences = sym_no_doublon(dictionnaire_cooccurrences)
	#print 'dictionnaire_cooccurrences'
	#afficher_dict(dictionnaire_cooccurrences,20)
	dictionnaire_cooccurrences_somme={}
	dictionnaire_cooccurrences_somme_quadratique={}
		
	for x,y in dictionnaire_cooccurrences.iteritems():
		dictionnaire_cooccurrences_somme[x[0]]=dictionnaire_cooccurrences_somme.get(x[0],0) + y
		dictionnaire_cooccurrences_somme_quadratique[x[0]]=dictionnaire_cooccurrences_somme_quadratique.get(x[0],0) + y*y
	print 'dictionnaire_cooccurrences_somme',len(dictionnaire_cooccurrences_somme.keys())#,dictionnaire_cooccurrences_somme
	#print 'dictionnaire_cooccurrences_somme',dictionnaire_cooccurrences_somme#,dictionnaire_cooccurrences_somme
	Nb_cooc=sum(dictionnaire_cooccurrences_somme.values())
	if type_biparti==False:
		Nb_cooc = Nb_cooc/2#divide by 2 because dictionnaire_cooccurrences is symmetric
	Nb_cooc2 = sum(dictionnaire_cooccurrences_somme.values())
	#print "Nb_cooc",Nb_cooc
	#print "Nb_cooc2",Nb_cooc2
	
	distance = {}
	if type_distance == 'raw':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:			
				#expected=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				distance[x] = y
	if type_distance == 'callon':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
				prod=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] 
				distance[x] =  float(y) / float(prod) * float(Nb_cooc)

	if type_distance == 'chi2':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if x[0]!=x[1]:			
				expected=dictionnaire_cooccurrences_somme[x[0]] / float(Nb_cooc) * dictionnaire_cooccurrences_somme[x[1]] 
				#if x[0]=='commentateur/individu':
				#	print x,y,dictionnaire_cooccurrences_somme[x[0]],dictionnaire_cooccurrences_somme[x[1]] ,Nb_cooc,expected

				if y>expected:					
					racine =  (y - expected) / math.sqrt(expected)
					#if x[0]=='commentateur/individu':
					#	print racine
					distance[x]=racine
					#print 'in',x,dictionnaire_cooccurrences_somme[x[0]],dictionnaire_cooccurrences_somme[x[1]],expected,y
				#else:
					#print 'too far away',x,dictionnaire_cooccurrences_somme[x[0]],dictionnaire_cooccurrences_somme[x[1]],expected,y

	if type_distance == 'Phi':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if x[0]!=x[1]:			
				expected=dictionnaire_cooccurrences_somme[x[0]] / float(Nb_cooc) * dictionnaire_cooccurrences_somme[x[1]] 
				if y>expected:					
					racine =  (y - expected) / (expected)
					distance[x]=racine
					#print 'in',x,dictionnaire_cooccurrences_somme[x[0]],dictionnaire_cooccurrences_somme[x[1]],expected,y
				#else:
					#print 'too far away',x,dictionnaire_cooccurrences_somme[x[0]],dictionnaire_cooccurrences_somme[x[1]],expected,y


	if type_distance == 'chi2_yates':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
				expected=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				if y>expected:
					racine =  math.pow(math.fabs(y - expected)-0.5,2) / expected
					distance[x]=racine

	if type_distance == 'PEM':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
				expected=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				ecart =  y - expected
				if ecart>0:
					ecart_max = min(dictionnaire_cooccurrences_somme[x[0]],dictionnaire_cooccurrences_somme[x[0]])-expected
					distance[x]=ecart/ecart_max

	if type_distance == 'cramer':#a bit tuned...
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
				expected=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				racine =  (y - expected) / math.sqrt(expected) / math.sqrt(expected)#math.sqrt(Nb_cooc)
				distance[x]=racine

	if type_distance == 'chi2_squared':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if x[0]!=x[1]:
				expected=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				if y>expected:
					racine =  math.pow(y - expected,2) / expected					
					distance[x]=racine


	if type_distance == 'chi2_complete':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
			
				x1,x2=x[0],x[1]
				x1_somme=dictionnaire_cooccurrences_somme[x1]
				x2_somme=dictionnaire_cooccurrences_somme[x2]
				x_not1_somme = Nb_cooc-x1_somme
				x_not2_somme = Nb_cooc-x2_somme
			
				observed11=y
				observed12=x1_somme - y
				observed21=x2_somme - y
				observed22 = Nb_cooc - (x1_somme+ x2_somme) + y
			 
				expected11 = x1_somme * x2_somme / float(Nb_cooc)
				expected12 = x1_somme * x_not2_somme / float(Nb_cooc)
				expected21 = x2_somme * x_not1_somme / float(Nb_cooc)
				expected22 = x_not1_somme  * x_not2_somme / float(Nb_cooc)
			
			
			
				chi2_11 =  math.pow(observed11 - expected11,2) / expected11
				chi2_12 =  math.pow(observed12 - expected12,2) / expected12
				chi2_21 =  math.pow(observed21 - expected21,2) / expected21
				chi2_22 =  math.pow(observed22 - expected22,2) / expected22
				#print 'chi2_11,chi2_12,chi2_21,chi2_22'
			
				racine = chi2_11+chi2_12+chi2_21+chi2_22
				#print x,racine
				distance[x]=racine


	if type_distance == 'cramer_complete':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:

				x1,x2=x[0],x[1]
				x1_somme=dictionnaire_cooccurrences_somme[x1]
				x2_somme=dictionnaire_cooccurrences_somme[x2]
				x_not1_somme = Nb_cooc-x1_somme
				x_not2_somme = Nb_cooc-x2_somme

				observed11=y
				observed12=x1_somme - y
				observed21=x2_somme - y
				observed22 = x1_somme+x2_somme-y
				observed22 = Nb_cooc - (x1_somme+ x2_somme) + y

				expected11 = x1_somme * x2_somme / float(Nb_cooc)
				expected12 = x1_somme * x_not2_somme / float(Nb_cooc)
				expected21 = x2_somme * x_not1_somme / float(Nb_cooc)
				expected22 = x_not1_somme  * x_not2_somme / float(Nb_cooc)


				chi2_11 =  (observed11 - expected11) / math.sqrt(expected11)/math.sqrt(Nb_cooc)
				chi2_12 =  (observed12 - expected12) / math.sqrt(expected12)/math.sqrt(Nb_cooc)
				chi2_21 =  (observed21 - expected21) / math.sqrt(expected21)/math.sqrt(Nb_cooc)
				chi2_22 =  (observed22 - expected22) / math.sqrt(expected22)/math.sqrt(Nb_cooc)
				#print 'chi2_11,chi2_12,chi2_21,chi2_22',chi2_11,chi2_12,chi2_21,chi2_22

				racine = chi2_11+chi2_12+chi2_21+chi2_22
				#print x,racine
				distance[x]=racine


	if type_distance == 'chi2_complete_yates':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
			
				x1,x2=x[0],x[1]
			
				x1_somme=dictionnaire_cooccurrences_somme[x1]
				x2_somme=dictionnaire_cooccurrences_somme[x2]
				x_not1_somme = Nb_cooc-x1_somme
				x_not2_somme = Nb_cooc-x2_somme

				observed11=y
				observed12=x1_somme - y
				observed21=x2_somme - y
				observed22 = Nb_cooc - (x1_somme+ x2_somme) + y

				expected11 = x1_somme * x2_somme / float(Nb_cooc)
				expected12 = x1_somme * x_not2_somme / float(Nb_cooc)
				expected21 = x2_somme * x_not1_somme / float(Nb_cooc)
				expected22 = x_not1_somme  * x_not2_somme / float(Nb_cooc)


				expected11=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				expected22=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)

				chi2_11 =  math.pow(math.fabs(observed11 - expected11)-0.5,2) / expected11
				chi2_12 =  math.pow(math.fabs(observed12 - expected12)-0.5,2) / expected12
				chi2_21 =  math.pow(math.fabs(observed21 - expected21)-0.5,2) / expected21
				chi2_22 =  math.pow(math.fabs(observed22 - expected22)-0.5,2) / expected22
				racine = chi2_11+chi2_12+chi2_21+chi2_22
				distance[x]=racine


	elif type_distance == 'weighted':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
			 	#distance[x] =  (y) / math.sqrt(dictionnaire_cooccurrences_somme[x[0]]  * dictionnaire_cooccurrences_somme[x[1]] )
				distance[x] =  float(y) / float(dictionnaire_cooccurrences_somme[x[1]])
				#print 'distance=',distance[x],'y:',y, ' divise par :',dictionnaire_cooccurrences_somme[x[1]]
	elif type_distance == 'cosine':
		dictionnaire_voisins=voisins(dictionnaire_cooccurrences)
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
				#print x,y,dictionnaire_voisins[x[0]],dictionnaire_voisins[x[1]],math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[0]]),math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[1]])
				prod_scalaire = sum(merge_support(dictionnaire_voisins[x[0]], dictionnaire_voisins[x[1]], lambda x,y: x*y).values())
				distance[x] =  float(prod_scalaire) / math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[0]]  * dictionnaire_cooccurrences_somme_quadratique[x[1]] )
				#print 'cosinus=',distance[x],'=prod_scalaire:',prod_scalaire, ' divise par :',math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[0]]  * dictionnaire_cooccurrences_somme_quadratique[x[1]] )

		# for x,y in dictionnaire_cooccurrences.iteritems():
		# 	distance[x] =  (y) / math.sqrt(dictionnaire_cooccurrences_somme[x[0]]  * dictionnaire_cooccurrences_somme[x[1]] )

	elif type_distance == 'cosine_chi2':
		dictionnaire_voisins=voisins(dictionnaire_cooccurrences)
		for x,y in dictionnaire_cooccurrences.iteritems():
			if [x[0]]!=[x[1]]:
				#print x,y,dictionnaire_voisins[x[0]],dictionnaire_voisins[x[1]],math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[0]]),math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[1]])
				prod_scalaire = sum(merge_support(dictionnaire_voisins[x[0]], dictionnaire_voisins[x[1]], lambda x,y: x*y).values())
				distance[x] =  float(prod_scalaire) / math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[0]]  * dictionnaire_cooccurrences_somme_quadratique[x[1]] )
				#print 'cosinus=',distance[x],'=prod_scalaire:',prod_scalaire, ' divise par :',math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[0]]  * dictionnaire_cooccurrences_somme_quadratique[x[1]] )

				#expected=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				#if y>expected:					
				#	racine =  (y - expected) / math.sqrt(expected)
				#	distance[x]=distance[x]+racine

	elif type_distance == 'mutual information':
		for x,y in dictionnaire_cooccurrences.iteritems():
			if x[0]!=x[1]:
				expected=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				mi = math.log(float(y) /float(expected))
				distance[x] =  mi
	elif type_distance == 'distributional':
		mi={}
		for x,y in dictionnaire_cooccurrences.iteritems():
			if x[0]!=x[1]:
				expected=dictionnaire_cooccurrences_somme[x[0]] * dictionnaire_cooccurrences_somme[x[1]] / float(Nb_cooc)
				mixy = math.log(float(y) /float(expected))
				if mixy>0:
					mi[x] =  mixy
		#fonctions.afficher_dict(mi)
		dictionnaire_voisins_mi=voisins(mi)
		for x in mi.keys():
			#print x,y,dictionnaire_voisins[x[0]],dictionnaire_voisins[x[1]],math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[0]]),math.sqrt(dictionnaire_cooccurrences_somme_quadratique[x[1]])
			numerateur = sum(merge_support(dictionnaire_voisins_mi[x[0]], dictionnaire_voisins_mi[x[1]], lambda x,y: min(x,y)).values())
			try:
				dist=float(numerateur) / (sum(dictionnaire_voisins_mi[x[0]].values())-mi[x])
			except:
				dist=0
			if dist>0:
				distance[x] =  dist


	return distance,dictionnaire_cooccurrences_somme

def get_occurrences(results1_top,rank=True):
	occ_dict1={}
	for id_art,liste_doublet in results1_top.iteritems():
		for elem in liste_doublet:
			if rank:
				occ_dict1[elem[0]]=occ_dict1.get(elem[0],0)+1
			else:
				occ_dict1[elem]=occ_dict1.get(elem,0)+1
	return occ_dict1


def tfidf_compute(biparti,rank=True):#biparti biparti[(x1,x2)]=nbre occurrences
	tfidf={}
	#print 'tfidf_compute'
	#print 'biparti'
	#afficher_dict(biparti,4)
	#print 'results1_top'
	#afficher_dict(results1_top,3)
	#print 'results2_top'
	#afficher_dict(results2_top,3)
	#print N_article
	biparti_dict=make_dict_dict_from_dict_doublet(biparti)
	#print 'biparti_dict',biparti_dict
	somme_occurrences={} 
	#print 'results1_top',results1_top

	#occ_dict1=get_occurrences(results1_top,rank=rank)
	#print 'results2_top',results2_top
	#occ_dict2=get_occurrences(results2_top,rank=rank)
	#print 'occ_dict1',occ_dict1
	#print 'occ_dict2',occ_dict2
	 
	#occ_dict=merge(occ_dict1,occ_dict2,lambda x,y:x+y)
	
	for x in biparti_dict:
		somme_occurrences[x]=sum(biparti_dict[x].values())
	N = float(sum(somme_occurrences.values()))
	
	#print 'somme_occurrences',somme_occurrences
	afficher_dict(somme_occurrences,2)
	
	#print 'N_article',N_article,somme_occurrences
	for x,dict_vois in biparti_dict.iteritems():#si on songe au tfidf entre un cluster et des journaux.
		tfidf[x]={}
		for y,occ in dict_vois.iteritems():
			#tf = float(occ)/float(somme_occurrences[y])#fréquence (ou plutôt ratio cooc/nb articles) du journal y dans le cluster x
			#idf = float(N_article)/float(somme_occurrences[x])#rareté du cluster/// NON il faut rareté du terme!!!
			tf = float(occ)#frequence brute d'apparition du journal dans le cluster
			idf = float(N/float(somme_occurrences[y]))#rareté du journal
			#print y
			#print 'y,tf,idf,tfidf',y,tf,float(somme_occurrences[y]),math.log(idf)
			tfidf[x][y]=tf*math.log(idf)
			#print x,y,float(occ),float(somme_occurrences[y]),tf,math.log(idf),tf*math.log(idf)#math.log(idf),tf*math.log(idf),somme_occurrences[y]
	return tfidf



def tf_compute(biparti,results1_top,results2_top,N_article):#biparti biparti[(x1,x2)]=nbre occurrences
	tfidf={}
	#print 'tfidf_compute'
	#print 'biparti'
	#afficher_dict(biparti,4)
	#print 'results1_top'
	#afficher_dict(results1_top,3)
	#print 'results2_top'
	#afficher_dict(results2_top,3)
	#print N_article
	biparti_dict=make_dict_dict_from_dict_doublet(biparti)
	somme_occurrences={} 
	#print 'results1_top',results1_top
	occ_dict1=get_occurrences(results1_top)
	occ_dict2=get_occurrences(results2_top)
	#print 'occ_dict1',occ_dict1
	occ_dict=merge(occ_dict1,occ_dict2,lambda x,y:x+y)
	somme_occurrences=occ_dict
	#print 'somme_occurrences'
	afficher_dict(somme_occurrences,2)
	
	#print 'N_article',N_article,somme_occurrences
	for x,dict_vois in biparti_dict.iteritems():
		#tfidf[x]={}
		for y,occ in dict_vois.iteritems():
			tf = float(occ)/float(somme_occurrences[y])
			idf = float(N_article)/float(somme_occurrences[x])
			if not y in tfidf:
				tfidf[y]={}
			tfidf[y][x]=tf*math.log(idf)
			
			#print x,y,float(occ),float(somme_occurrences[y]),tf,math.log(idf),tf*math.log(idf)#math.log(idf),tf*math.log(idf),somme_occurrences[y]
	return tfidf



def compute_final_net(biparti,distance_type,distance_thres,top_edges,k_nearest,type_biparti):	
	
	distance_bip,dictionnaire_cooccurrences_somme= distance(biparti,distance_type,type_biparti)
	#print distance_bip
	try:
		distance_bip = extractabove_thres(distance_bip,distance_thres)
	except:
		pass
	try:
		distance_bip = extractNtop(distance_bip,top_edges)
	except:
		pass	
	try:
		final_net = extractNnearest(distance_bip,k_nearest)
	except:
		pass
	print 'final_net'
	afficher_dict(final_net,5)
	
	return final_net,dictionnaire_cooccurrences_somme

	
#fonctions destinés à récupérer les données dans la bdd:
def get_results(tablesource,curs, where=None,rank=None,unicity=False):	
	if where==None:
		if rank==None:
			try:
				results = curs.execute(" SELECT file,id,data FROM " +tablesource ).fetchall()#cited journal
			except:
				results = curs.execute(" SELECT id,data FROM " +tablesource ).fetchall()#cited journal
		else:
			try:
				results = curs.execute(" SELECT file,id,rank,parserank,data FROM " +tablesource ).fetchall()#cited journal
			except:
				results = curs.execute(" SELECT id,rank,parserank,data FROM " +tablesource ).fetchall()#cited journal
	else:
		if type(where)==str:
			if rank==None:
				try:
					results = curs.execute(" SELECT file,id,data FROM " +tablesource + " where data = '" + where +"'" ).fetchall()#cited journal
				except:
					results = curs.execute(" SELECT id,data FROM " +tablesource + " where data = '" + where +"'" ).fetchall()#cited journal
			else:
				try:
					results = curs.execute(" SELECT file,id,rank,parserank,data FROM " +tablesource + " where data = '" + where +"'" ).fetchall()#cited journal
				except:
					results = curs.execute(" SELECT id,rank,parserank,data FROM " +tablesource + " where data = '" + where +"'" ).fetchall()#cited journal
		else:
			where= "('"+"','".join(where)+"')"
			print " SELECT file,id,data FROM " +tablesource + " where id in " + where
			if rank==None:
				try:
					results = curs.execute(" SELECT file,id,data FROM " +tablesource + " where id in " + where  ).fetchall()#cited journal
				except:
					results = curs.execute(" SELECT id,data FROM " +tablesource + " where id in " + where  ).fetchall()#cited journal
			else:
				try:
					results = curs.execute(" SELECT file,id,rank,parserank,data FROM " +tablesource + " where id in " + where  ).fetchall()#cited journal
				except:
					results = curs.execute(" SELECT id,rank,parserank,data FROM " +tablesource + " where id in " + where  ).fetchall()#cited journal
	dict = {}
	if len(results[0])%2==0:
		cle_index=0
	else:
		cle_index=1
	for result in results:
		#cle='_'.join(list(map(str,result[:2])))
		cle=int(result[cle_index])
		if rank==None:
			try:
				dict.setdefault(cle,[]).append(unicode(str(result[-1]).strip(),'utf-8'))
			except:
				dict.setdefault(cle,[]).append(unicode(str(result[-1]),'utf-8'))
			if unicity:
				dict[cle]=unique(dict[cle])
		else:
			data=unicode(str(result[-1]),'utf-8')
			if len(data)>0:
				if not cle in dict:
					dict[cle]={}
				if not data in dict[cle]:
					try:
						dict[cle][data.strip()]={}
					except:
						dict[cle][data.strip()]={}
				try:
					dict[cle][data.strip()].setdefault(result[-3],[]).append(result[-2])
				except:
					dict[cle][data.strip()].setdefault(result[-3],[]).append(result[-2])
				if unicity:
					dict[cle][data][result[-3]]=[0]
	return dict


def get_connect(dbname):
	conn = sqlite3.connect(dbname)
	conn.text_factory = OptimizedUnicode
	conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
	cur = conn.cursor()
	return conn,cur


def get_select(dbname,tablesource, curs,fields=" file,id,data ", where= ' '):
	print " SELECT  " +fields+ ' FROM ' + tablesource + where
	results = curs.execute(" SELECT  " +fields+ ' FROM ' + tablesource + where ).fetchall()#cited journal
	return results
	
def get_data(dbname,table,limit_id=None):
	clause=0
	fields=('id','file','rank','parserank','data')
	sql= 'SELECT ' + ','.join(fields) + ' FROM '+table
	if not limit_id==None:
		sql = sql + ' limit ' + str(limit_id)
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()
	try:
		res = conn.execute(sql)
	except:
		clause=1
		fields=('id','rank','parserank','data')
		sql= 'SELECT ' + ','.join(fields) + ' FROM '+table
		if not limit_id==None:
			sql = sql + ' limit ' + str(limit_id)
		res = conn.execute(sql)
	conn.commit()
	data={}
	for row in res:
		dico={}
		if clause==0:
			dico['file']=row[1]
			dico['rank']=row[2]
			dico['parserank']=row[3]
			dico['data']=row[4]
		else:
			dico['rank']=row[1]
			dico['parserank']=row[2]
			dico['data']=row[3]
		data.setdefault(row[0],[]).append(dico)
	return data

def afficher_dict(dict,limit=10000000000):
	i=0
	print '### display first entries (1000 first char) of the dict featuring ', len(dict.keys()), ' total entries'
	for cle,valeur in dict.iteritems():
		i+=1
		if i<limit:
			print '###### ',cle,'\t',str(valeur)[:1000]
		
def inverse_dict_year(years_bins_dict):
	years_bins_dict_inv={}
	for periode,years_bins in years_bins_dict.iteritems():
		for y in years_bins:
			years_bins_dict_inv.setdefault(y,[]).append(periode)
	return years_bins_dict_inv

def filter_yera(results,result_pubdate,years_bins_dict,years_bins_dict_inv):
	results_y = {}
	#inverse_dict_year(years_bins_dict)
	for cle, data in results.iteritems():
		y= result_pubdate[cle]
		for periode in years_bins_dict_inv.get(int(y),[]):
			if not periode in results_y:
				results_y[periode]={}
			results_y[periode][cle]=data
		# 	
		# 
		# for periode,years_bins in years_bins_dict.iteritems():
		# 	if int(y) in years_bins:
		# 		if not periode in results_y:
		# 			results_y[periode]={}
		# 		#	temp={}
		# 		#else:
		# 		#	temp =results_y[periode]
		# 		#temp[cle] = data
		# 		results_y[periode][cle]=data
		# 		#results_y[periode] = temp
	return results_y

def extract_data(table1source,result_pubdate,years_bins_dict,years_bins_dict_inv,curs,where=None,rank=None,unicity=False):
	results1 = get_results(table1source,curs,where=where,rank=rank,unicity=unicity)
	results1_y = filter_yera(results1,result_pubdate,years_bins_dict,years_bins_dict_inv)
	return results1_y

def first4(string):
	return string[:4]

def filter_indexs(dictionnary,key_list):
	dictionnary_filtered={}
	if len(dictionnary.keys())>len(key_list):
		for key in key_list:
			if key in dictionnary:
				dictionnary_filtered[key]=dictionnary[key]
	else:
		for key in dictionnary:
			if key in key_list:
				dictionnary_filtered[key]=dictionnary[key]
	return dictionnary_filtered

def count_dist(years_cover,dict_type=False,normalisation=False,idf=False):
	years_cover_dist={}
	for x in years_cover:
		if dict_type:#on rajoute le nombre d'éléments par item
			years_cover_dist[x] = years_cover_dist.get(x,0)+len(years_cover[x])
		else:
			years_cover_dist[x] = years_cover_dist.get(x,0)+1
	if normalisation:
		years_cover_dist_norm=normalize(years_cover_dist)
		if idf:
			for x,y in years_cover_dist_norm.iteritems():
				years_cover_dist[x] = - math.log(y)
	return years_cover_dist



def cut_time(curs,nb_quantile = 1,cut_type='regular',period_size=None,overlap_size=None):
	result_pubdate=get_results('ISIpubdate',curs)
	#print 'result_pubdate',result_pubdate
	result_pubdate_short={}
	for x,y in result_pubdate.iteritems():
		#result_pubdate_short['_'.join(x.split('_')[:2])] = y[0][:4]#plus prudent de prendre les 4 premiers caractères de la date.
		result_pubdate_short[x] = y[0][:4]#plus prudent de prendre les 4 premiers caractères de la date.
	result_pubdate=result_pubdate_short
	#print 'result_pubdate',result_pubdate
	#print result_pubdate.values()
	try: 
		int(str(nb_quantile))==int(nb_quantile)
		years_cover = list(map(int,list(map(first4,result_pubdate.values()))))
		#print 'years_cover',years_cover
		years_cover.sort()
		#print 'quant'
		years_cover_dist = count_dist(years_cover)
		#print 'years_cover_dist',years_cover_dist
		print 'cut_type',cut_type
		if cut_type=='homogeneous':
			#print years_cover_dist
			ymin= min(years_cover_dist.keys())
			ymax =max(years_cover_dist.keys())
			borders=[]
			#print range(ymin,ymax)
			#print years_cover
			for i in range(nb_quantile):
				borders.append(int(quantile(years_cover, float((i))/float(nb_quantile))))

			borders.append(ymax+1)
			#print 'borders'+str(borders)
			years_bins=[]
			for i in range(len(borders)-1):
				if len(range(borders[i],borders[i+1]))>0:
					years_bins.append(range(borders[i],borders[i+1]))
			#print 'years_bins',years_bins
		elif cut_type=='regular':
			ymin= min(years_cover_dist.keys())
			ymax =max(years_cover_dist.keys())
			nb_quantile = min(ymax-ymin+1,nb_quantile) 
			print 'nb_quantile',nb_quantile
			longueur = (ymax-ymin+1)/nb_quantile
			years_bins=[]
			for i in range(nb_quantile):
				years_bins.append(range(ymax+1-longueur,ymax+1))
				ymax=ymax-longueur
		#print 'years_bins',years_bins
		years_bins_overlap=[]
		#print 'ici',period_size
		if not period_size==None:# and 
			if not overlap_size==None :
				#print 'years_bins',years_bins
				for ibegin in range((len(years_bins)-overlap_size)/(period_size-overlap_size)):
					years_bins_overlap.append(years_bins[ibegin*(period_size-overlap_size):ibegin*(period_size-overlap_size)+period_size])
					#for delta_overlap in range(overlap_size+1):
					#	periodi=[]
					#	years_bins_overlap.append(years_bins[ibegin*period_size+delta_overlap:ibegin*period_size+delta_overlap+period_size])
				years_bins=[]
				#print 'years_bins_overlap',years_bins_overlap
				for x in years_bins_overlap:
					period_y = []
					for xx in x:
						for h in xx:
							period_y.append(h)
					years_bins.append(period_y)
				#print 'years_bins',years_bins
	except: 
		years_bins=nb_quantile
	years_bins_dict ={}
	for x in years_bins:
		years_bins_dict[str(x[0])+'_'+str(x[-1])] = x
	#afficher_dict(years_bins_dict)
	
	print 'periodes:',years_bins_dict.keys()
	return years_bins_dict,result_pubdate


def extract_high_level_network(G,communities,label_nb=2):
	hl_network={}

	#build dictionnary of nodes' communities 
	node2com_binary={}
	com2node_binary={}
	#print 'communities',communities
	for i,community in enumerate(communities):
		for node in community:
			node2com_binary[node]=i
			com2node_binary.setdefault(i,[]).append(node)
	#first compute the dictionnary of distance of each node in the communities
	import networkx as nx
	node2com_probabilitic={}
	inbound_links={}
	# print 'G.nodes()',len(G.nodes())
	for node1, neighbours in zip(G.nodes(),G.adjacency_list()):
		
		node2com_probabilitic[node1]={}
		if len(neighbours)>0:
			pass
		else:
			neighbours=[node1]
		for node2 in neighbours:
			try:
				comm2 = node2com_binary[node2]
				if not comm2 in inbound_links:
					inbound_links[comm2]={}
				try:
					weight = G[node1][node2]['weight']
					try:
						weight = math.sqrt(weight*G[node2][node1]['weight'])	#on fait la moyenne géométrique des liens entrants/sortants pour avoir des labels "medians""
					except:
						weight = 0.01
				except:
					weight=1#case where single communities are found
					
					
				
				
				node2com_probabilitic[node1][comm2]=node2com_probabilitic[node1].get(comm2,0.)+weight
				inbound_links[comm2][node1]=inbound_links[comm2].get(node1,0.)+weight
			except:
				pass
	# print 'inbound_links',len(inbound_links.keys())
	# print 'inbound_links',len(unique(inbound_links.keys()))
	#print 'node2com_probabilitic',node2com_probabilitic
	for x in node2com_probabilitic:
		print x, sum(node2com_probabilitic[x].values()),node2com_probabilitic[x]
	#compute the label of communities given the degree of belongings:
	communities_label={}
	i=0
	for community, nodes_neighbours_links in inbound_links.iteritems():
		#communities_label[community] = ' & '.join(map(str,extractNtop(filter_indexs(nodes_neighbours_links,com2node_binary[community]),label_nb).keys()))
		i+=1
		res=' & '.join(map(str,extractNtop(filter_indexs(nodes_neighbours_links,com2node_binary[community]),label_nb).keys()))
		if res in communities_label.values():
			res=res + '_bis'
			if res in communities_label.values():
				res=res + '_bis'	
				if res in communities_label.values():
					res=res + '_bis'	
					if res in communities_label.values():
						res=res + '_bis'	
		# print i,res
		communities_label[community] = res

	# print 'communities_label',len(communities_label.keys())
	# print 'communities_label',len(communities_label.values())	
	# 
	# print 'communities_label',len(unique(communities_label.values()))	
	# print 'node2com_probabilitic',len(node2com_probabilitic.keys())
	# print 'node2com_probabilitic',len(unique(node2com_probabilitic.values()))
	
	node_belongings_top2={}
	#print 'node2com_probabilitic',node2com_probabilitic
	for node, comm_neighbours_links in node2com_probabilitic.iteritems():
		l=comm_neighbours_links.items()
	#	print l
		if len(l)>0:
			l.sort(key=itemgetter(1),reverse=True)
			somme = sum(map(lambda x: x[1],l))
			somme_top=0.
			i=0
			while somme_top<.6:
				#print somme_top
				#print i
				if i>0:
					if l[i][1]<l[i-1][1]/4:
						somme_top=1.
					else:
						somme_top=1.
				else:
					node_belongings_top2.setdefault(node,[]).append(l[i])
					somme_top+=l[i][1]/somme
					i=i+1	
			#print node_belongings_top2
	#print 'node_belongings_top2',node_belongings_top2
	
	#then build the higher level communities network
	G_high=nx.Graph()
	compt=0
	for community in communities:#compulsory, some high level nodes may be forgoten otherwise
		for node in community:
			compt+=1
			try:
				G_high.add_node(communities_label[node2com_binary[node]])
			except:
				pass
	
	# print 'G_high',len(G_high.nodes())
	
	
	for community, nodes_neighbours_links  in inbound_links.iteritems():
		comm1=deepcopy(community)
		community=communities_label[community]
		if community not in G_high.nodes():
			G_high.add_node(community)
		for node,weight in nodes_neighbours_links.iteritems():
			try:
				#print 'list',com2node_binary[comm1]
				#print 'w',weight,len(com2node_binary[comm2]),len(com2node_binary[comm1]),float(len(com2node_binary[comm2])*len(com2node_binary[comm1]))
				comm2 = communities_label[node2com_binary[node]]
				#print com2node_binary[node2com_binary[node]]
				#print 'w',weight,len(com2node_binary[node2com_binary[node]]),float(len(com2node_binary[node2com_binary[node]])*len(com2node_binary[comm1]))
				if not comm2 in G_high.nodes():
					G_high.add_node(comm2)
				try:
					G_high[community][comm2]['weight']=G[community][comm2]['weight']+weight / float(len(com2node_binary[node2com_binary[node]])*len(com2node_binary[comm1]))
				except:
					G_high.add_edge(community,comm2)
					#print float(len(com2node_binary[comm2])*len(com2node_binary[community]))
					G_high[community][comm2]['weight']=weight / float(len(com2node_binary[node2com_binary[node]])*len(com2node_binary[comm1]))
			except:
				pass

		
	com2node_probabilitic={}
	for node,projection in node2com_probabilitic.iteritems():
		for comm,weight in projection.iteritems():
			if node in communities[comm]:
				com2node_probabilitic.setdefault(comm,[]).append((node,weight))
				
	com2node_probabilitic_norm={}
	for comm,nodes_prob in com2node_probabilitic.iteritems():
		somme = sum(map(lambda x : x[1],nodes_prob))
		dict_temp={}
		for nodespro in nodes_prob:
			dict_temp[nodespro[0]]=nodespro[1]/somme
		com2node_probabilitic_norm[comm]=dict_temp
	#print 'com2node_probabilitic',com2node_probabilitic
	return G_high,communities_label,com2node_probabilitic_norm



def reconstruct_kclique(affiliation):
	k_clique_comm_enriched={}
	for x,y in affiliation.iteritems():
		k_clique_comm_enriched.setdefault(y,[]).append(x)
	return k_clique_comm_enriched.values()

def	extend_communities(edges_list,k_clique_comm):
	affiliations={}
	seuil=0.5
	for i,comm in enumerate(k_clique_comm):
		for node in comm:
			affiliations[node]=i
	reseau={}
	for edge in edges_list:
		edgev=edge.split()
		reseau.setdefault(int(edgev[0]),[]).append((int(edgev[1]),float(edgev[2])))
	for i in range(1):#on fait 3 passes successives d'extension des communautés
		for node,voisins in reseau.iteritems():
			if not node in affiliations:
				affil_voisins = list(map(lambda x: (affiliations.get(x[0],-1),x[1]),voisins))
				dico_affil=somme_dict(affil_voisins)
				if i>4:
					try:
						del(dico_affil[-1])
					except:
						pass
				#print dico_affil
				l=dico_affil.items()
				l.sort(key=itemgetter(1),reverse=True)
				if l[0][1]/sum(dico_affil.values())>seuil:
					affiliations[node]=l[0][0]
	k_clique_comm_enriched = reconstruct_kclique(affiliations)
	return k_clique_comm_enriched


def somme_dict(liste):
	dico={}
	for x in liste:
		dico[x[0]]=dico.get(x,0.)+x[1]
	return dico

def prone_graph(G,thres):
	compteur_delete=0
	for u,v in G.edges():
		if G[u][v]['weight']<thres:
			G.remove_edge(*(u,v))
			compteur_delete+=1
			#print '(u,v) retire'
	print compteur_delete, ' edges deleted'
	return G

def get_rid_of_attributes(G):
	Gc=deepcopy(G)
	label_nodes={}
	nodes_label={}
	i=0
	for node in G.nodes():
		i+=1
		G.remove_node(node)
		G.add_node(str(node))
		label_nodes[str(node)]=str(i)
		nodes_label[str(i)]=unicode(str(node))###pb with accents!!!
		
	G.add_edges_from(Gc.edges())
	for edge in G.edges():
		try:
			G[edge[0]][edge[1]]['weight']=Gc[edge[0]][edge[1]]['weight']
		except:
			pass
	import networkx as nx
	Gr=nx.relabel_nodes(G,label_nodes)
	return Gr,nodes_label
	
def symmetrize(G):
	import networkx as nx
	Gs = nx.Graph()
	for x in G.nodes():
		Gs.add_node(x) 
	for node1, neighbours in zip(G.nodes(),G.adjacency_list()):
		for node2 in neighbours:
			#print node1,node2
			try:
				w=G[node1][node2]['weight']
			except:
				w=1.
			try:
				winv=G[node2][node1]['weight']
			except:
				winv=0.
			#print w,winv
			Gs.add_edge(node1, node2)
			Gs[node1][node2]['weight']=float(w + winv)/2. 
	return Gs
	
def	detect_community(G,community_detection_method,explorer=False,filter_max=False,max_size=1):
	
	if community_detection_method=='clique percolation':
		import percolation
		edges_list,index= get_edges_list(G)

		try:
			k = k_nearest
			k_clique_comm = percolation.launch_percolation(edges_list,k)
			print 'lclique',k,len(k_clique_comm)
			while len(k_clique_comm)<3 and k>3:
				k=k-1
				k_clique_comm = percolation.launch_percolation(edges_list,k)
				print 'lclique',k,len(k_clique_comm)
		except:
			k_clique_comm = percolation.launch_percolation(edges_list,3)
			if len(k_clique_comm)<5:
				print 'up'
				k_clique_comm = percolation.launch_percolation(edges_list,4)
		k_clique_comm = extend_communities(edges_list,k_clique_comm)
		#print str(len(k_clique_comm)) + ' communities'
		communities=[]

		for comm in k_clique_comm:
			communities.append(list(map(lambda x:index[x],list(comm))))
		#print communities
	if community_detection_method=='infomap':
		import uuid
		import networkx as nx
		import random
		unique_filename = str(uuid.uuid4())
		#unique_filename="e1c40fb5-ddf0-4ac7-ae39-2838413d1cc5"
		infomap_dir='infomap_dir'
		if 'srv/local/web/cortext/manager/' in os.getcwd():
			infomap_dir='infomap_dir_unix'
		if  'iscpif/users/cointet/' in os.getcwd():
			infomap_dir='infomap_dir_iscpif'
		graph_file_name = infomap_dir+'/graphs/' + unique_filename
		graph_file_name_net = infomap_dir+'/graphs/' + unique_filename + '.net'
		
		print 'graph_file_name',graph_file_name
		Gr,nodes_label=get_rid_of_attributes(G)
		nx.write_pajek(Gr, graph_file_name, encoding='UTF-8')
		import commands
		print "sed '1d' " + graph_file_name + ' > '+graph_file_name+'2'
		commands.getstatusoutput("sed '1d' " + graph_file_name + ' > '+graph_file_name+'.net')
		seed = random.randint(1,999999)
		print 'infomap_dir/'+'infomap ' + str(seed) + ' ' + graph_file_name_net + ' '+ str(10)
		commands.getstatusoutput(infomap_dir+'/'+'infomap ' + str(seed) + ' ' + graph_file_name_net + ' '+ str(10))
		file = open(infomap_dir+'/graphs/'+unique_filename+'.tree')
		lignes = file.readlines()
		partition={}
		for ligne in lignes[1:]:
			comm = int(ligne.split(':')[0])
			node = ligne[:-1].split(' ')[-1].replace('"','')
			partition[nodes_label[node]]=comm
		communities={}
		for noeud,comm in partition.iteritems():
			communities.setdefault(comm,[]).append(noeud)
		communities=communities.values()
		print commands.getstatusoutput('rm infomap_dir/graphs/'+unique_filename + '*')
		
	if community_detection_method=='louvain':
		import louvain
		if not explorer:
			try:				
				G=prone_graph(G,filter_max)
				print 'filtered at threshold:',filter_max
			except:
				pass
			if 1:
				if G.is_directed():
					print 'ok cool'
					Gs=symmetrize(G)
				else:
					Gs=G
				partition = louvain.best_partition(Gs)
			else:
				partition={}
				for i,x in enumerate(G.nodes()):
					partition[x]=i
			communities={}
			for noeud,comm in partition.iteritems():
				communities.setdefault(comm,[]).append(noeud)
			communities=communities.values()
			#print 'communities finalnumber', len(communities)
		elif explorer=='max':
			communities_filtered_list=[]
			communities_filtered_list_size=[]
			G2 = deepcopy(G)
			steps=50
			for thres_range in range(steps):
				thres=float(thres_range)/float(steps)
				G2=prone_graph(G2,thres)
				try:
					partition = louvain.best_partition(G2)
				except:
					partition={}
					for i,x in enumerate(G2.nodes()):
						partition[x]=i
				communities={}
				for noeud,comm in partition.iteritems():
					communities.setdefault(comm,[]).append(noeud)
				communities=communities.values()
				taille_dist=[]
				
				for co in communities:
					taille_dist.append(len(co))
				
				N = float(sum(taille_dist))
				camille=0
				for taille in taille_dist:
					camille = camille + math.pow(float(taille)/N,2)
				
				taillemax = max(taille_dist)
				david=0
				for taille in taille_dist:
					david += math.pow(taille,2) - math.pow(taillemax,2)
				
				
				communities_filtered=[comm for comm in communities if len(comm)>max_size]#communities of unique nodes are excluded
				#print thres,'\t', len(communities),'\t',len(communities_filtered)
				cover=0
				for co in communities_filtered:
					cover +=len(co)
				dist_taille_norm = count_dist(taille_dist,normalisation=True)
				#print taille_dist,dist_taille_norm
				entropy = 0
				for nb,val in dist_taille_norm.iteritems():
					entropy-=nb*val*math.log(val)
					
					
				
				communities_filtered_list_size.append(cover*len(communities_filtered))
				communities_filtered_list.append(communities_filtered)
				print float(thres_range),'\t',float(len(communities_filtered)),'\t',float(cover),'\t',float(cover*len(communities_filtered))	,'\t',entropy,'\t',camille			,'\t',david			
			indexmax = max([i for i,x in enumerate(communities_filtered_list_size) if x == max(communities_filtered_list_size)])#communities_filtered_list_size.index(max(communities_filtered_list_size))
			# print [i for i,x in enumerate(communities_filtered_list_size) if x == max(communities_filtered_list_size)]
			# print indexmax
			# print communities_filtered_list_size[indexmax]
			communities=float(indexmax)/float(steps)#on optimise sur le nombre de communautes * la couverture 
			#communities=float(max(0,communities_filtered_list_size.index(max(communities_filtered_list_size))-1))/float(steps)
		elif explorer=='all':
			communities_filtered_list=[]
			communities_filtered_list_size=[]
			G2 = deepcopy(G)
			steps=100
			for thres_range in range(steps):
				thres=float(thres_range)/float(steps)
				G2=prone_graph(G2,thres)
				try:
					partition = louvain.best_partition(G2)
				except:
					partition={}
					for i,x in enumerate(G2.nodes()):
						partition[x]=i
				communities={}
				for noeud,comm in partition.iteritems():
					communities.setdefault(comm,[]).append(noeud)
				communities=communities.values()
				#communities_filtered=[comm for comm in communities if len(comm)>1]#communities of unique nodes are excluded
				#print thres,'\t', len(communities),'\t',len(communities_filtered)
				communities_filtered=communities
				cover=0
				for co in communities_filtered:
					cover +=len(co)
				communities_filtered_list_size.append(len(communities_filtered))
				communities_filtered_list.append(communities_filtered)
				print thres_range,'\t',len(communities_filtered),'\t'
	return communities

def getmin(communities_filtered_list_size):
	minimum=8
	indexf=0
	clause=0
	for index,item in enumerate(communities_filtered_list_size):
		if item<minimum and clause==0:
			print 'found a minpartition of size ',item
			clause=1
			indexf=index
	return indexf
			
def getmax(communities_filtered_list_size):
	maximum=50
	indexf=0
	itemmem=0
	for index,item in enumerate(communities_filtered_list_size):
		if item<maximum and item>itemmem:
			indexf=index
			itemmem=item
	print 'found a maxpartition of size ',communities_filtered_list_size[indexf]
	return indexf

#############################################################################
#############################################################################
#################################-FILE PROCESSING-###########################
#############################################################################
#############################################################################



class dialect(csv.excel):
	delimiter = '\t'
	skipinitialspace = False
	quotechar = '"'
	doublequote = False
	lineterminator='\n'
	quoting = False

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]


def read_tab(file):
	input = open(file)
	dico,dico_inv={},{}
	for ligne in input.readlines():
		ligne=ligne[:-1]
		ligne_v=ligne.split('\t')
		dico.setdefault(ligne_v[0],[]).append(ligne_v[1])
		dico_inv.setdefault(ligne_v[1],[]).append(ligne_v[0])
	return dico,dico_inv
#############################################################################
#############################################################################
#################################-FIND & OPERAT-#############################
#############################################################################
#############################################################################


def find_key(dic, val):
    """return the key of dictionary dic given the value"""
    return [k for k, v in dic.iteritems() if v == val][0]


def list_nested(cle_occ):
	candidates=cle_occ
	#print 'candidates_occ_dict',candidates_occ_dict
	candidates_size_dict,frozen_dict={},{}
	for x in cle_occ:
		x_frozen=frozenset(x.split(' '))
		candidates_size_dict[x]=len(x_frozen)
		frozen_dict[x]=x_frozen
	l=candidates_size_dict.items()
	l.sort(key=itemgetter(1),reverse=False)

	nested={}#nested[x]=x+y
	subnested={}
	#a optimiser
	#print "candidates.keys()",candidates.keys()
	for i,x in enumerate(l[:-1]):
		(x,x_size)=x
		for y in l[i+1:]:
			(y,y_size)=y
			if y_size>x_size:
				if frozen_dict[x].issubset(frozen_dict[y]):
					nested.setdefault(x,[]).append(y)
					subnested.setdefault(y,[]).append(x)
	return candidates_size_dict,nested,subnested


#############################################################################
#############################################################################
#################################-FONCTIONS BDD-#############################
#############################################################################
#############################################################################

def connexion(name_bdd):
	connection = sqlite3.connect(name_bdd)
	connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")
	cursor = connection.cursor()
	ex = connection.execute
	return connection,ex

def safe_execute(cur, query):
    try:
        cur.execute(query)
        print('Executed query: %s' % query)
    except:
        print('Not Executed query: %s' % query)
        pass	

def list_tables(output_file):
	conn,curs=connexion(output_file)
	tables_list= conn.execute("SELECT * FROM sqlite_master")
	list_tab = []
	for tables in tables_list:
		print tables
		if tables[0]=='table':
			list_tab.append(tables[1])
	return list_tab
	
def count_rows(name_bdd,table):
	connection,ex = connexion(name_bdd)
	sortie= ex("SELECT COUNT(*)  from " +table).fetchall()
	#print '\n' + "comptage de l evolution du nombre de " +champ_nom + " "+ str(champ_val) + " de la table " + table +  " dans la bdd " +name_bdd +'\n'
	connection.close()	
	return sortie[0][0]

def remplir_table_fast(name_bdd,name_table,champs_liste,champs_name):
	connection, ex = connexion(name_bdd)
	sql_insert =  'INSERT OR IGNORE INTO ' + name_table+' '+ champs_name + " VALUES("  + ','.join(['?'] * (len(champs_liste[0]))) + ")"	
	connection.executemany(sql_insert,champs_liste)
	# for champ in champs_liste: 
	# 	ex(sql_insert,champ)
	connection.commit()
	connection.close()
	print "      + table " + name_table+" being populated"

def create_table(table_name,conn,curs,fields=' ( file text, id integer, rank integer DEFAULT 0 NOT NULL, parserank integer DEFAULT 0 NOT NULL, data text) ',erase=True):
 	if erase:
		try:	
			curs.execute('drop table ' + table_name )
			print 'table',table_name,'erased'
		except:
			print 'table',table_name,' absent'
			pass					
	try:
		curs.execute('create table ' + table_name  + fields)
		print ' created table ', table_name

	except:
		print 'unable to create table ', table_name
		pass

	
#############################################################################
#############################################################################
#################################-PARSING FONCT-#############################
#############################################################################
#############################################################################
def afficher_champ(y):
   chaine = ''
   for x in y:
      chaine = chaine + str(x)+'\n' 
   return chaine

def afficher_notices(notices,dico_tag,first=1):
   mapping_complet={}
   for index in notices.keys()[1:first+1]:
      notice=notices[index]
      print ('\n******************')
      print ('notice number: ' + str(index))
      for x,y in notice.iteritems():
         if 'uuu' in x:
            try:
               print ('field ' + (str(dico_tag[x.split('uuu')[0]][0])+'_'+x.split('uuu')[1]).replace(' ','') + ':\t' + afficher_champ(y))
               mapping_complet[x]=(str(dico_tag[x.split('uuu')[0]][0])+'_'+x.split('uuu')[1]).replace(' ','')
            except:
               pass
         else:    
            print ('field ' + str(dico_tag.get(x,[x])[0]) + ':\t' + afficher_champ(y))
            mapping_complet[x]=str(dico_tag.get(x,[x])[0])			
   return mapping_complet

def getlower(string):
	return string.lower()

def insert_notices(bdd_name,reinit_db,notices,dico_tag,mapping_complet,corpus_name,output_type,first=0):
	conn,curs=create_bdd(bdd_name)
	if output_type=='reseaulu':
		tables={}
		idx=0
		for index, notice in notices.iteritems():
			idx+=1
			if idx%100000==0:
				print 'already ',idx,' indexed notices. '
			#if index<=first:
			for x,y in notice.iteritems():
				#on recupere le nom des tables
				if 'uuu' in x:
					table_name = str(dico_tag.get(x.split('uuu')[0],[x])[0])+'_'+x.split('uuu')[1]
				else:
					table_name = str(dico_tag.get(x,[x])[0])
				for rank in range(len(y)):
					for parserank in range(len(y[rank])):
						if not table_name in tables:
							tables[table_name] = []
						temp = tables[table_name]
						if table_name in ['ISIAUTHOR']:
							temp.append([str(corpus_name)]+list(map(getlower,list(map(str,[idx+first,rank,parserank,y[rank][parserank].replace('\"',"")])))))
						else:
							if table_name in ['ISISC']:
								temp.append(list(map(unicode,[corpus_name,idx+first,rank,parserank,y[rank][parserank].replace('\"',"")[5:]])))
							else:
								temp.append(list(map(unicode,[corpus_name,idx+first,rank,parserank,y[rank][parserank].replace('\"',"")])))
						tables[table_name] = temp				
		for table_name in tables.keys():
			if reinit_db and first==0:
				try: 
					print 'try to drop table ' + table_name
					curs.execute('drop table ' + table_name)
					print 'sucess ' + table_name
				except:
					print 'cound not drop table ' + table_name
					pass
			try:
				curs.execute('create table ' + table_name  + ' (file text, id integer, rank integer, parserank integer, data text)')
			except:
				pass
			sql_insert =  'INSERT OR IGNORE INTO ' + table_name+ " VALUES("  + ','.join(['?'] * (5)) + ")"
			for ligne in tables[table_name]:
				#print sql_insert,ligne
				curs.execute(sql_insert,ligne)
			print 'table ' + table_name +' created and populated'

	if output_type=='rdf':
		pass

	if output_type=='standard':
		if reinit_db:
			try:
				curs.execute('drop table notices')	
			except:
				pass
		curs.execute("CREATE TABLE notices (id INTEGER PRIMARY KEY)")
		champs_name=''
		for x,y in mapping_complet.iteritems():

			sql = "ALTER TABLE notices ADD COLUMN "+ y +" TEXT"
			curs.execute(sql)
			champs_name = champs_name+y+','
		champs_name='(' + champs_name[:-1] + ')'
		for index, notice in notices.iteritems():
			#if index<=first:
			champs_name=[]
			for x in notice.keys():
				champs_name.append(mapping_complet[x])
			champs_name = '(' + ','.join(champs_name) +')'
			sql_insert =  'INSERT OR IGNORE INTO notices ' + champs_name + " VALUES("  + ','.join(['?'] * (len(notice))) + ")"
			curs.execute(sql_insert,string_version(notice.values()))
		print  'table notices created and populated'
	conn.commit()
	conn.close()	




class Notice:
	UT=''

class Place:
	city=''

def clean_inst(chaine):
	if chaine[:3]=='c1 ':
		chaine =chaine[3:]
	return chaine

def clean_country(chaine):
	zipcode=''
	state=''
	if len(chaine)>0:
		if chaine[-1]=='.':
			chaine =chaine[:-1]
		chaine=chaine.strip()
		if len(chaine)==2:
			#print chaine
			state=chaine
			country='usa'
		else:
			chainev= chaine.split(' ')
			tryint = chainev[-1]
			try:
				if str(int(tryint)) in str(tryint):
					country='usa'
					zipcode = str(int(tryint))
					if len(chainev)>1:
						if len(chainev[0])==2:
							state = chainev[0]
			except:
				pass

		if chaine=='australi':
			country='australia'
		if chaine=='russia' or chaine=='ussr' :
			country = 'russia'
		#	print chaine
		if 'china' in chaine or chaine=='peoples r c'  or chaine=='peoples r' or chaine=='peoples r chin':
			country='china'
		if chaine=='wales' or chaine=='eng' or chaine=='north ireland' or chaine=='scotland' or chaine=='england':
			country='uk'
		try:
			country=country.lower()
		except:
			country=chaine
	return country,zipcode,state


def find_zipcode(chaine):
	try:
		m=re.search(figure_regular,chaine)
		#print m.group(0)[1:]
		return m.group(0).split('-')[1]
	except:
		return ''


def find_zipcode_noncomplet(chaine):
	try:
		m=re.search(figure_regular_noncomplet,chaine)
		return m.group(0)
	except:
		return ''

def find_zipcode_complet(chaine):
	try:
		m=re.search(figure_regular_complet,chaine)
		return m.group(0)
	except:
		return ''

def find_nofigure(chaine):
	try:
		if not re.search(number,chaine)==None:
			m=re.search(figure,chaine)
			#print m
			return m.group(0)
		else:
			return chaine
	except:
		return ''

def morethanone(chaine):
	if len(chaine)>1:
		return chaine
	else:
		return ''

def clean_city(chaine):
	zipcode2 = find_zipcode_complet(chaine)
	#print chaine,'zipcode2',zipcode2
	if len(zipcode2)>0:
		i=chaine.find(zipcode2)
		#print chaine,i,len(zipcode2)
		chaine=chaine[0:i]+chaine[i+len(zipcode2):]
		city=chaine.strip()
		zipcode2 = zipcode2.split('-')[-1]
	else:
		#print chaine
		zipcode2=find_zipcode_noncomplet(chaine)
		if len(zipcode2)>0:
			i=chaine.find(zipcode2)
			#print chaine,i,len(zipcode2)
			chaine=chaine[0:i]+chaine[i+len(zipcode2):]
			city=chaine.strip()
			zipcode2 = zipcode2.split('-')[-1]

			#print city,'zipcode2',zipcode2
		else:
			city=chaine
	#print 'city1',city

	city=find_nofigure(city).strip()
	city=' '.join(map(lambda x:morethanone(x),city.strip().split(' '))).strip()
	#print 'city2',city
	if 'amsterdam' in city:
		city='amsterdam'

	return city,zipcode2

import re
number = "\\d"
numbered = "\\d+"

numbers = "\\b\\d+\\b"
figure = "\\b[a-zA-Z ]+\\b"
figure_tiret = "[a-zA-Z]+-\\d+\\b"
figure_complet = "[a-zA-Z]+-\\d+\\b"
#figure = "\\d+"
number = re.compile(number)
numbered = re.compile(numbered)
figure_regular_noncomplet = re.compile(numbers)
figure = re.compile(figure)
figure_regular = re.compile(figure_tiret)
figure_regular_complet = re.compile(figure_complet)














def clean_inst(chaine):
	if chaine[:3]=='c1 ':
		chaine =chaine[3:]
	return chaine

# def clean_country(classe_countries,chaine):
# 
# 	#print chaine
# 	if len(chaine)>0:
# 		if chaine[-1]=='.':
# 			chaine =chaine[:-1]
# 		if chaine.lower()=='australi':
# 			chaine='australia'
# 		if chaine.lower()=='russia' or chaine.lower()=='ussr' :
# 			chaine = 'russia'
# 		if chaine[-3:]=='USA' or chaine.lower()=='baja ca':
# 			chaine = 'USA'
# 		#	print chaine
# 		if 'china' in chaine.lower() or chaine.lower()=='peoples r c'  or chaine.lower()=='peoples r' or chaine.lower()=='peoples r chin':
# 			chaine='china'
# 		if chaine.lower()=='wales' or chaine.lower()=='eng' or chaine.lower()=='north ireland' or chaine.lower()=='scotland' or chaine.lower()=='england':
# 			chaine='UK'
# 		tryint = chaine.split(' ')[-1]
# 	
# 		try:
# 		#	print str(int(tryint))
# 			if str(int(tryint)) in str(tryint):
# 				chaine='USA'
# 		except:
# 			pass
# 		chaine=chaine.lower()
# 		chaine = classe_countries.get(chaine,chaine)
# 	#print '\t'+chaine
# 	return chaine
# 

import re
numbers = " \\d+|\\d+ "
figure_regular_noncomplet = re.compile(numbers)
def find_zipcode_noncomplet(chaine):
	try:
		m=re.search(figure_regular_noncomplet,chaine)
		#print m
		return m.group(0)
	except:
		return ''

def remove_numbers(chaine):
	chaine = ' '+chaine+' '
	zipcode2=find_zipcode_noncomplet(chaine)
	#print zipcode2
	if len(zipcode2)>0:
		i=chaine.find(zipcode2)
		#print chaine,i,len(zipcode2)
		chaine=chaine[0:i]+chaine[i+len(zipcode2):]
		city=chaine.strip()
		zipcode2 = zipcode2.split('-')[-1]
	else:
		city=chaine
	return city.strip()

def complete_db(bdd_name,reinit_db,dico_tag,mapping_complet,corpus_name,corpus_type):
	classe_countries={}
	conn,curs=create_bdd(bdd_name)
	if corpus_type=='isi':
		for table_name in ['ISICR','ISIC1_1']:
				if table_name == 'ISICR':
					dict={}
					dict_id={}
					########RAJOUTER UN ISICRDOI!!!!!
					for parse_rank,tbl_name_out in enumerate(['ISICRAuthor','ISICRYear','ISICRJourn']):
						try:
							curs.execute('drop table ' + tbl_name_out )
						except:
							pass
						try:	
							curs.execute('create table ' + tbl_name_out  + ' (file text, id integer, rank integer, parserank integer, data text)')
						except:
							pass
						if tbl_name_out in ["ISICRAuthor"]:#,'ISIkeyword','ISIID'
							curs.execute("INSERT INTO "+tbl_name_out+" SELECT file,id,rank,parserank,lower(data) FROM " +table_name +' where parserank =' + str(parse_rank))
						else:
							curs.execute("INSERT INTO "+tbl_name_out+" SELECT file,id,rank,parserank,data FROM " +table_name +' where parserank =' + str(parse_rank))
						results = curs.execute(" SELECT file,id,rank,data FROM " +table_name +' where parserank =' + str(parse_rank)).fetchall()
						for result in results:
							if tbl_name_out=='ISICRJourn':
								cited_journ= str(result[3]).strip()
								if len(remove_numbers(cited_journ))>0:
									dict.setdefault('_'.join(list(map(str,result[:3]))),[]).append(str(result[3]).strip())
							else:		
								dict.setdefault('_'.join(list(map(str,result[:3]))),[]).append(str(result[3]).strip())
					conn.commit()	
					create_table('ISICitedRef',conn,curs)
					for cle, valeur in dict.iteritems():
						data= "("+ "'" + "','".join(cle.split('_')) + "','" + str('_'.join(valeur)) + "')"
						#print data
						#cur2.execute("UPDATE billets SET date=? WHERE id=?", (ts, article_id))
						data_v=cle.split('_')
						data_v.append(str('_'.join(valeur)))
						#print data_v
						curs.execute("INSERT INTO ISICitedRef ('file','id','rank','data') VALUES (?,?,?,?)", data_v)
					conn.commit()	

					print 'ISICR processed'
				if table_name == 'ISIC1_1':
					create_table('ISIC1City',conn,curs)
					create_table('ISIC1Country',conn,curs)
					create_table('ISIC1Inst',conn,curs)
					create_table('ISIC1State',conn,curs)
					create_table('ISIC1Zip',conn,curs)
					results = curs.execute(" SELECT file,id,rank,data FROM " +table_name).fetchall()
					dict={}
					for result in results:
						dict.setdefault('_'.join(list(map(str,result[:3]))),[]).append(str(result[3]))
					adresse_complete={}
					for cle,val in dict.iteritems():
						#print cle, val
						adresse_complete=', '.join(val)
						C1vv=adresse_complete
						C1v=adresse_complete.lower().split(', ')

						country,zipcode,state = clean_country(C1v[-1])
						lab = C1v[0]
						if country=='canada':
							city,zipcode2 = clean_city(C1v[-3])
						else:
							if country=='brazil' and (len(C1v)>4 or C1v[-2]=='sp' or C1v[-2]=='df') and len(C1v[-2].split())==1:
								city,zipcode2 = clean_city(C1v[-3])
							else:	
								city,zipcode2 = clean_city(C1v[-2])
						if zipcode=='':
							if zipcode2!='':
								zipcode=zipcode2
							else:
								zipcode=find_zipcode(C1vv)
						countryv=country.split()
						if 'usa' in country:
							if len(countryv[0])==2:
								country='usa'
								state=countryv[0]
							if len(countryv)==3:#mi 48202 usa
								zipcode=countryv[1]

						if country=='uk':
							#print C1v[-2]
							zipcode3=C1v[-2].split(city)[-1].strip()
							if len(zipcode3)>0:
								zipcode=zipcode3
						if country=='brazil' and (len(C1v)>4 or C1v[-2]=='sp' or C1v[-2]=='df') and len(C1v[-2].split())==1:# or  (country=='brasil' and len(C1v)>4):#UNIV TORONTO, DEPT BOT, TORONTO M5S 3B2, ONTARIO, CANADA
							state = C1v[-2].strip().split('-')[0]
						if country=='canada':# or  (country=='brasil' and len(C1v)>4):#UNIV TORONTO, DEPT BOT, TORONTO M5S 3B2, ONTARIO, CANADA
							state= C1v[-2].strip()
							statev=state.split()
							if len(statev)>1:
								zipcode=' '.join(statev[1:]).strip()
								state=statev[0].strip()
							else:
								try:
									zipcode=C1v[-3].split(city)[-1].strip()
								except:
									pass
						newplace=Place()
						newplace.country=country
						newplace.state=state
						newplace.city=city
						newplace.lab=lab
						newplace.zipcode=zipcode
						newplace.c1=C1vv
						try:
							x=int(country[0])
							#print 'country',country
						except:
							try:
								x=int(country[-1])
							except:
								data= "("+ "'" + "','".join(cle.split('_')) + "','" + newplace.lab + "')"
								curs.execute("INSERT INTO ISIC1Inst ('file','id','rank','data') VALUES " + data)
								data= "("+ "'" + "','".join(cle.split('_')) + "','" + newplace.country + "')"
								curs.execute("INSERT INTO ISIC1Country ('file','id','rank','data') VALUES " + data)
								data= "("+ "'" + "','".join(cle.split('_')) + "','" + newplace.city + "')"
								curs.execute("INSERT INTO ISIC1City ('file','id','rank','data') VALUES " + data)
								data= "("+ "'" + "','".join(cle.split('_')) + "','" + newplace.state + "')"
								curs.execute("INSERT INTO ISIC1State ('file','id','rank','data') VALUES " + data)
								data= "("+ "'" + "','".join(cle.split('_')) + "','" + newplace.zipcode + "')"
								curs.execute("INSERT INTO ISIC1Zip ('file','id','rank','data') VALUES " + data)
								
								# 	data= "("+ "'" + "','".join(cle.split('_')) + "','" + countr + "')"
								# 	#print data
								# 	curs.execute("INSERT INTO ISIC1Country ('file','id','rank','data') VALUES " + data)
								# 	data= "("+ "'" + "','".join(cle.split('_')) + "','" + str(valeur[0]).lower() + '_' + countr+ "')"
								# 	curs.execute("INSERT INTO InstCountry ('file','id','rank','data') VALUES " + data)
								# conn.commit()	
								# print 'ISIC1 processed'
								#'ISICitedRef'
						
						#adresse_complete.setdefault(cle,[]).append(', '.join(val))
						
					#print adresse_complete
						
						
					# results = curs.execute(" SELECT file,id,rank,data FROM " +table_name).fetchall()
					# dict={}
					# for result in results:
					# 	dict.setdefault('_'.join(list(map(str,result[:3]))),[]).append(str(result[3]))
					# create_table('ISIC1Inst',conn,curs)
					# create_table('ISIC1Country',conn,curs)
					# create_table('InstCountry',conn,curs)
					# for cle, valeur in dict.iteritems():
					# 	countr=clean_country(classe_countries,str(valeur[-1])).lower()
					# 	data= "("+ "'" + "','".join(cle.split('_')) + "','" + clean_inst(str(valeur[0]).lower()) + "')"
					# 	curs.execute("INSERT INTO ISIC1Inst ('file','id','rank','data') VALUES " + data)
					# 	data= "("+ "'" + "','".join(cle.split('_')) + "','" + countr + "')"
					# 	#print data
					# 	curs.execute("INSERT INTO ISIC1Country ('file','id','rank','data') VALUES " + data)
					# 	data= "("+ "'" + "','".join(cle.split('_')) + "','" + str(valeur[0]).lower() + '_' + countr+ "')"
					# 	curs.execute("INSERT INTO InstCountry ('file','id','rank','data') VALUES " + data)
					conn.commit()	
					print 'ISIC1 processed'
					#'ISICitedRef'
	if corpus_type=='factiva':
		months = lambda a, b: abs((a.year - b.year) * 12 + a.month - b.month)
		
		for table_name in ['region','publicationDate']:
			print 'ininis'
			print table_name
			if table_name=='publicationDate':
				import time
				from datetime import date
				date_begin = datetime.date(1990, 1, 1)
				results = curs.execute(" SELECT file,id,rank,parserank,data FROM " +table_name).fetchall()
				dict_date={}
				for result in results:
					pubdate=map(lambda x: int(x),result[4].split('T')[0].split('-'))
					date_now = datetime.date(pubdate[0], pubdate[1], pubdate[2])
					#dict_date.setdefault('_'.join(list(map(str,result[:4]))),[]).append(str(months(date_now,date_begin)))
					# print "new couple", date_now,date_begin
					# print (date_now-date_begin).days
					# print (date_now-date_begin).days/7
					dict_date.setdefault('_'.join(list(map(str,result[:4]))),[]).append(str(int((date_now-date_begin).days*12/365)))

				create_table('ISIpubdate',conn,curs)
				for cle, valeur in dict_date.iteritems():
					data= "("+ "'" + "','".join(cle.split('_')) + "','" + str('_'.join(valeur)) + "')"
					data_v=cle.split('_')
					data_v.append(str('_'.join(valeur)))
					#print data_v
					curs.execute("INSERT INTO ISIpubdate ('file','id','rank','parserank','data') VALUES (?,?,?,?,?)", data_v)
				conn.commit()	
			if table_name=='region':
				results = curs.execute(" SELECT file,id,rank,parserank,data FROM " +table_name).fetchall()
				dict_region_simple={}
				dict_region_regions={}
				dict_region_countries={}
				for result in results:
					chaine  = result[4]
					# print chaine
					# print chaine.split('/Regions')
					# print chaine.split('Countries/')
					if 'Countries/' in  chaine[:10]:
						dict_region_countries.setdefault('_'.join(list(map(str,result[:4]))),[]).append(chaine.split('Countries/')[1])
					elif '/Regions' in chaine[-10:]:
						dict_region_regions.setdefault('_'.join(list(map(str,result[:4]))),[]).append(chaine.split('/Regions')[0])
					else:
						dict_region_simple.setdefault('_'.join(list(map(str,result[:4]))),[]).append(chaine)
				
				create_table('region_simple',conn,curs)
				create_table('region_regions',conn,curs)	
				create_table('region_countries',conn,curs)	
				for cle, valeur in dict_region_simple.iteritems():
					data= "("+ "'" + "','".join(cle.split('_')) + "','" + str('_'.join(valeur)) + "')"
					data_v=cle.split('_')
					data_v.append(str('_'.join(valeur)))
					curs.execute("INSERT INTO region_simple ('file','id','rank','parserank','data') VALUES (?,?,?,?,?)", data_v)
				for cle, valeur in dict_region_regions.iteritems():
					data= "("+ "'" + "','".join(cle.split('_')) + "','" + str('_'.join(valeur)) + "')"
					data_v=cle.split('_')
					data_v.append(str('_'.join(valeur)))
					curs.execute("INSERT INTO region_regions ('file','id','rank','parserank','data') VALUES (?,?,?,?,?)", data_v)
				for cle, valeur in dict_region_countries.iteritems():
					data= "("+ "'" + "','".join(cle.split('_')) + "','" + str('_'.join(valeur)) + "')"
					data_v=cle.split('_')
					data_v.append(str('_'.join(valeur)))
					curs.execute("INSERT INTO region_countries ('file','id','rank','parserank','data') VALUES (?,?,?,?,?)", data_v)
	elif corpus_type=='xmlpubmed':
		for table_name in ['Pubdate']:
			if table_name=='Pubdate':
				tbl_name_out = 'ISIpubdate'
 				try:		
					curs.execute('drop table ' + tbl_name_out )
				except:
					pass
				try:
					create_table(tbl_name_out,conn,curs)	
					#curs.execute('create table ' + tbl_name_out  + ' (file text, id integer, rank integer, parserank integer, data text)')
				except:
					pass
				print 'try to build ISIpubdate'
				#curs.execute("INSERT INTO "+tbl_name_out+" SELECT file,id,0,0,data FROM " +table_name +' where parserank =0')
				#conn.commit()
				datadate=get_select(bdd_name,'Pubdate', curs,fields=" file,id,data ", where= ' where parserank=0 ')
				dates=[]
				for data in datadate:
					try:
						if str(int(data[2][:4]))==data[2][:4]:
							dates.append([data[0],data[1],data[2][:4]])
					except:
						pass
				sql_insert =  'INSERT INTO ' + tbl_name_out+' '+ " (file,id,data) " + " VALUES("  + ','.join(['?'] * (len(dates[0]))) + ")"	
				conn.executemany(sql_insert,dates)
				conn.commit()
					


				