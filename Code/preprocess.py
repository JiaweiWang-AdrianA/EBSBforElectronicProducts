import json
import re
import os
from string import digits

def MW_Tokenizer(source):
	"""extract model words from source
	   input: an source(title/description),
	   output: the model words of this profile"""
	model_word=[]
	numpattern = re.compile('[0-9]+')
	for string in source:
		temstr = string.split(' ')
		#print(temstr)
		for w in temstr:
			#the model words must have at least one digit character and one non-digit character
			if len("".join(filter(str.isdigit, w)))>0 and len(w.translate(str.maketrans('', '', digits)))>0:
				match_string=re.search(numpattern, w)
				if match_string:
					s,e=match_string.span()
					mw=w[s:]
					if w[s:] not in model_word and bool(re.search('[^\d]',w.replace('.',''))) and bool(re.search('[^\d]',w.replace(',',''))):
						if len(w)>1:
							while w[-1]=='-':
								w=w[:-1]
							while w[0]=='-':
								w=w[1:]
						model_word.append(w)
	return model_word

def lower(text):
	"""lower the words in text"""
	if isinstance(text,list):
		texts=[]
		for t in text:
			t=lower(t)
			if t:
				texts.append(t.replace('\n','').replace(':',''))
		return texts
	elif isinstance(text,str):
		text=text.lower().replace('\n','').replace(':','')
		return text.strip()
	else:
		print('lower error')

def source_process(source,new_source):
	"""process the source"""
	if isinstance(source,list):
		for s in source:
			source_process(s,new_source)
	elif isinstance(source,str):
		if source and source.strip()!='' and source not in new_source:
			new_source.append(source.lower())

def clean_uselessword(source,uselesswords_list):
	new_source=[]
	for word in source:
		if word not in uselesswords_list:
			new_source.append(word)
	return new_source

def pre_process(product_id,product,brand):
	"""preprocess the data set"""
	syns=',;\'"、!@#$%^()[]+~*|&/'

	mw_synonyms={}
	with open('./MWSynonymsDict/MWSynonymsDict.json') as f:
		mw_synonyms=json.load(f)

	new_product={}
	for k in product:
		if k in ['<page title>','mfr part number','part','part number','manufacture','manufacturer','manufacturer part number','mfg model','model','model name','product model','product name','description','product description','description technical detail']:
			source=[]
			source_process(product[k],source)
			
			source=' '+''.join(source)+' '
			source=source.replace('\n','')
			
			#clean url
			urls=[product_id.split('//')[0],product_id.split('//')[0].replace('www.','')]
			for url in urls:
				source=source.replace(url,' ')

			#clean special symbol
			for syn in list(syns):
				source=source.replace(syn,' ')
				
			#clean uselessword		
			source=' '+source+' '
			if MW_Tokenizer([brand]):
				source=source.replace(brand,' ')
			source=source.replace(' 720p ',' ')
			source=source.replace(' 1080p ',' ')
			source=source.replace('2711p','2711')
			source=' '+source+' '

			words=['.com','.ca',' slr ','cm ','mp ','megapixel ',' 3d ','lcd-','ctr-','led-','tft-','display','in ','inch ','hz ','bit ','mm ','-series']
			for w in words:
				source=source.replace(w,' ')

			source=source.replace('s.master',' ')
			for w in ['-','.',':']:
				source=source.replace(' '+w,' ')
				source=source.replace(w+' ',' ')

			flag=True
			while flag:
				#remove the screen aspect ratio and resolution
				r=re.search(' \d+(\.\d+)?[:x]{1}\d+(\.\d+)?([:x]{1}\d+(\.\d+)?)? ',source)
				if r:
					string=source[r.span()[0]:r.span()[1]]
					source=source.replace(string,' ')
				else:
					flag=False

			flag=True
			while flag:
				#remove weight
				r=re.search(' [\.\d]+g ',source)
				if r:
					string=source[r.span()[0]:r.span()[1]]
					source=source.replace(string,' ')
				else:
					flag=False

			flag=True
			while flag:
				#remove time
				r=re.search(' [\d]{1,2}ms ',source)
				if r:
					string=source[r.span()[0]:r.span()[1]]
					source=source.replace(string,' ')
				else:
					flag=False

			flag=True
			while flag:
				#remove memory
				r=re.search(' [\d]{1,3}[mg]{1}b ',source)
				if r:
					string=source[r.span()[0]:r.span()[1]]
					source=source.replace(string,' ')
				else:
					flag=False

			flag=True
			while flag:
				#remove interface
				r=re.search(' [\d]?[x]?(hdmi)?(vga)?(dvi)?(usb)?(type-c)?(micro usb)?(mini usb)?(rs232)?(rs-232)?(rs-232c)?(rs422)?(rs485)?(ohc24)? ',source)
				if r:
					string=source[r.span()[0]:r.span()[1]]
					source=source.replace(string,' ')
				else:
					flag=False

			#try to create mw
			if k=='<page title>' and not MW_Tokenizer([source]):
				r1=re.search('[a-z]+ [\d]+',source)
				if r1:
					string=source[r1.span()[0]:r1.span()[1]]
					source=source.replace(string,string.replace(' ',''))

			#translate the mw based the mw synonymous dictionary
			source=' '+source+' '
			for mws in mw_synonyms:
				if mws in source:
					goal=MW_Tokenizer(sorted(mw_synonyms[mws]+[mws]))[0]
					if goal!=mws:
						#print(mws,'->',goal)
						source=source.replace(mws,goal)
						break

			new_product[k]=source.strip()
			
	return new_product

def MatchBrand(products):
	"""match the brand for each product"""
	Brands={}
	with open('Brands.json','r') as f:
		Brands=json.load(f)
	brands,pds_with_bds,pds_without_bds,bds=dict(),dict(),dict(),dict()
	for pid in sorted(list(products.keys())):
		candidate={}
		v=14
		for pkey in ['brand','brand name','manufacturer','manufacture','<page title>','mfr part number','part','part number','manufacturer part number','model','model name','product model','product name','description','product description','description technical detail']:
			if pkey in products[pid].keys() and products[pid][pkey]!='oem':
				for brand in sorted(list(Brands.keys())):
					for bd in Brands[brand]:
						if bd==products[pid][pkey] or bd+"'s"==products[pid][pkey]:
							if brand in candidate:
								candidate[brand]+=v//5
							else:
								if pkey=='brand' or pkey=='brand name':
									candidate[brand]=15
								elif pkey=='manufacture' or pkey=='manufacturer':
									candidate[brand]=7
								elif pkey=='<page title>':
									candidate[brand]=3
								else:
									candidate[brand]=1
			v-=1
		if candidate:
			brand=sorted(candidate.items(),key = lambda x:x[1],reverse = False)[0][0]
			brands[pid]=brand
			if brand in pds_with_bds.keys():
				pds_with_bds[brand][pid]=dict(products[pid])
			else:
				pds_with_bds[brand]=dict()
				pds_with_bds[brand][pid]=dict(products[pid])
			if brand in bds:
				bds[brand].append(pid)
			else:
				bds[brand]=[pid]
			continue

		flag=False
		title=products[pid].get('<page title>')
		for wo in title.split(' '):
			if flag:
				break
			for brand in sorted(list(Brands.keys())):
				if wo in Brands[brand]:
					brands[pid]=brand
					if brand in pds_with_bds.keys():
						pds_with_bds[brand][pid]=dict(products[pid])
					else:
						pds_with_bds[brand]=dict()
						pds_with_bds[brand][pid]=dict(products[pid])
					if brand in bds:
						bds[brand].append(pid)
					else:
						bds[brand]=[pid]
					flag=True
					break
		if flag:
			continue
		copy_p=products[pid].copy()
		copy_p.pop('<page title>')
		new_source=[]
		source_process(list(copy_p.values()),new_source)
		description=' '.join(new_source)
		for source in [title,description]:
			source=' '+source+' '
			for brand in sorted(list(Brands.keys())):
				for bd in Brands[brand]:
					if (' '+bd+' ') in source or (' '+bd+"'s") in source:
						if ('for '+bd+' ') in source:
							break
						if brand in candidate:
							candidate[brand]+=1
						else:
							if source==' '+title+' ':
								candidate[brand]=5
							else:
								candidate[brand]=1
		if candidate:
			brand=sorted(candidate.items(),key = lambda x:x[1],reverse = False)[0][0]
			brands[pid]=brand
			if brand in pds_with_bds.keys():
				pds_with_bds[brand][pid]=dict(products[pid])
			else:
				pds_with_bds[brand]=dict()
				pds_with_bds[brand][pid]=dict(products[pid])
			if brand in bds:
				bds[brand].append(pid)
			else:
				bds[brand]=[pid]
		else:
			pds_without_bds[pid]=products[pid]
	del products
	return (brands,pds_with_bds,pds_without_bds,bds)

