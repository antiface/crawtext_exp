import os
import whoosh
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED

class MySchema_isi(SchemaClass):
	PT=TEXT(stored=True)
	J9=TEXT(stored=True)
	SO=TEXT(stored=True)
	PY=NUMERIC(stored=True)
	VL=TEXT(stored=True)
	SC=TEXT(stored=True)
	UT=ID(stored=True,unique=True)
	TI=TEXT(stored=True)
	BP=ID(stored=True)
	DT=ID(stored=True)
	DE=TEXT(stored=True)
	ID=TEXT(stored=True)
	AB=TEXT(stored=True)
	CR=TEXT(stored=True)
	AU=TEXT(stored=True)
	C1 =TEXT(stored=True)
	CO =TEXT(stored=True)
	AF =TEXT(stored=True)
	C1uuu1 =TEXT(stored=True)
	C1uuu0 =TEXT(stored=True)	
	RP=TEXT(stored=True)
	FU =TEXT(stored=True)
	TC =TEXT(stored=True)
	BP =TEXT(stored=True)
	DI =TEXT(stored=True)
	T9 =TEXT(stored=True)


def instantiate(result_path,mapping_complet,corpus_type, reinit_db,name):
	print 'whoosh being instantiated'
	if reinit_db:
		if corpus_type=='isi':
			schema = MySchema_isi()
		else:
			print 'ici\n' + corpus_type
			fields={}
			print mapping_complet.keys()
			for i,key in enumerate(mapping_complet.keys()):
				if key=='ISIpubdate':
					fields[str(key)]=NUMERIC(stored=True)
				elif key=='accessionNo':
					fields[str(key)]=ID(stored=True,unique=True)
				else:
					fields[str(key)]=TEXT(stored=True)
				fields['CO']=TEXT()
			print 'whoosh fields',fields.keys()

			schema = Schema(**fields)
		
		import shutil
		if reinit_db==True:
			try:
				shutil.rmtree(os.path.join(result_path,'indexdir'+'_'+name))
				print 'rep indexdir deleted'
			except:
				pass
		try:
			os.mkdir(os.path.join(result_path,'indexdir'+'_'+name))
			print 'on a cree ',os.path.join(result_path,'indexdir'+'_'+name)

		except:
			pass
		ix = create_in(os.path.join(result_path,'indexdir'+'_'+name), schema)
	else:
		from whoosh.index import open_dir
		try:
			ix = open_dir(os.path.join(result_path,'indexdir'+'_'+name))
		except:
			reinit_db=True
			ix=instantiate(result_path,mapping_complet,corpus_type, reinit_db,name)
		
	return ix

def get_simple(notice,tag,type='string'):
	try:
		if type=='unicode':
			return 	unicode(notice.get(tag,'')[0][0])
		elif type=='numeric':
			return int(notice.get(tag,'')[0][0])
		elif type=='listing' or type=='keywords':
			return unicode(';'.join(notice.get(tag,'')[0]))
		elif type=='region':
			#print unicode(';'.join(map(lambda x : x[0],notice.get(tag,''))))
			return unicode(';'.join(map(lambda x : x[0],notice.get(tag,''))))
		elif type=='listing_CR':
			CR=[]
			for x in notice[tag]:
				CR.append(', '.join(x))
			return unicode(';'.join(CR))
	except:
		return None



def seed_se(ix,notices,corpus_type):
	#fonctions.afficher_dict(notices,2)
	from whoosh.filedb.multiproc import MultiSegmentWriter

	#ix = index.open_dir("indexdir")
	#writer = MultiSegmentWriter(ix, procs=1, limitmb=2000)#ROUND TO 100 !!!
	writer = ix.writer(procs=1, limitmb=2000)
	index_notice=0
	if corpus_type=='isi':
		text_simple=['J9 ','SO ','TI ','AB ','UT ','BP ','DT ','VL ','RP ','FU ','TC ','BP ','SC ','DI ','T9 ']
		numeric_simple=['PY ']
		keywords=['SC ','ID ','DE ']
		listing=['AU ','AF ']####MISIING FAU'CR ',

		listing_CR=['CR ','C1 uuu1',"C1 uuu0"]
		content = ['TI ','AB ','ID ','DE ','SC ']
		types={}
		for tag in numeric_simple:
			types[tag]='numeric'
		for tag in text_simple:
			types[tag]='unicode'
		for tag in listing:
			types[tag]='listing'
		for tag in listing_CR:
			types[tag]='listing_CR'
		for tag in keywords:
			types[tag]='keywords'
		for notice in notices.values():
			index_notice+=1
			if not index_notice%500 or index_notice==len(notices.keys()):
				print ( str(index_notice)  + ' records indexed by whoosh ')

			notice_fields={}
			for tag in text_simple + numeric_simple+listing+listing_CR+keywords:
				res=get_simple(notice,tag,types[tag])
				#print tag
				if not res==None:
					#print tag,res
					if len(tag)==3:
						tag=tag[:2]
					else:
						tag=tag.replace(" ",'')
					#print tag
					notice_fields[tag]=res
					if tag+' ' in content:
						notice_fields.setdefault('CO',[]).append(res)
			if 'CO' in notice_fields:
				notice_fields['CO']='. '.join(notice_fields['CO'])
				notice_fields['_stored_CO']=u''
			#print 'notice_fields',notice_fields
				#writer.add_document(title=u"Title to be indexed", _stored_title=u"Stored title")
			#print 'notice_good',notice_good
			writer.add_document(**notice_fields)
	else:
		print '\n'
		types={}
		types['region']='region'
		types['ISIpubdate']='numeric'
		types['company']='region'
		types['industry']='region'
		
		#pubmed oriented: 
		types['MeshHeading']='listingCR'
		types['Chemical']='listingCR'
		types['Author']='listingCR'
		types['DateCompleted']='listingCR'
		types['DateCreated']='listingCR'
		types['Grant']='listingCR'
		types['MedlineJournalInfo']='listingCR'
		types['MeshHeading']='listingCR'
		types['NameOfSubstance']='listingCR'
		types['PublicationType']='listingCR'
		types['RefSource']='listingCR'


		add_doc=0
		accno=[]
		for notice in notices.values():
			index_notice+=1
			if not index_notice%500 or index_notice==len(notices.keys()):
				print index_notice,  ' records indexed by whoosh '
			notice_good={}
			for key in notice.keys():
				res=get_simple(notice,key,type=types.get(key,'unicode'))
				notice_good[str(key)]=res
				notice_good.setdefault('CO',[]).append(res)
			if 'CO' in notice_good:
				#print notice_good['CO']
				notice_good['CO']='. '.join(map(lambda x: unicode(x),notice_good['CO']))
				notice_good['_stored_CO']=u''
			
			writer.add_document(**notice_good)
			add_doc +=1
			#print 'add_doc',add_doc,
			#accno.append(notice_good['accessionNo'])
		#print 'len(accno)',len(accno)
		#for ac in accno:
		#	print accno.count(ac)
	writer.commit()

