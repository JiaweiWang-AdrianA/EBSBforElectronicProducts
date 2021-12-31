import os
import json
import re
from string import digits


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def lower(text):
	"""delete the words in text"""
	if isinstance(text,list):
		texts=[]
		for t in text:
			t=lower(t)
			if t:
				texts.append(t)
		return texts
	elif isinstance(text,str):
		text=text.lower()
		return text.strip()
	else:
		print('lower error')


def prestring(string):
	string=string.replace('|',' ')
	string=string.replace('(',' ')
	string=string.replace(')',' ')
	string=string.replace(',',' ')
	string=string.replace('"',' ')
	string=string.replace('\'',' ')
	string=string.replace('\n',' ')
	string=string.replace('\t',' ')
	if string[-4:]=='#aba':
		string=string[:-4]
	while '  ' in string:
		string=string.replace('  ',' ')
	return string


def ismodelword(w):
	if len(w)<4:
		return False
	if w in ['3m','3d','720p','1080p','2711p','rs-232','ohc24','2xhdmi']:
		return False
	for word in ['1024','1920','1080']:
		if word in w:
			return False
	if w.count('.')>1:
		return False

	endwords=['.com','.ca','slr','cm','mm','ms','mp','megapixel','display','in','inch','hz','bit','cd','cc','year','years']
	for word in endwords:
		partlen=0-len(word)
		if w[partlen:]==word and (len(w)-len(word)<5 or is_number(w[:partlen])):
			return False
	#startwords=['lcd-','ctr-','led-','tft-','megapixel','ohc','rs','win']
	startwords=['lcd','ctr','led','tft','megapixel','ohc','rs','win','lcd-','ctr-','led-','tft-','ohc-','rs-','win-']
	for word in startwords:
		partlen=len(word)
		if w[:partlen]==word and (len(w)-len(word)<5 or is_number(w[partlen:])):
			return False
	#get brands
	brands={}
	with open('../brands.json') as f:
		brands=json.load(f)
	if w in brands:
		return False

	numpattern = re.compile('[0-9]+')
	w=w.replace('-','')
	w=w.replace(':','')
	numpattern = re.compile('[0-9]+')
	if len("".join(filter(str.isdigit, w)))>0 and len(w.translate(str.maketrans('', '', digits)))>0:
		match_string=re.search(numpattern, w)
		if match_string:
			if bool(re.search('[^\d]',w.replace('.',''))) and bool(re.search('[^\d]',w.replace(',',''))) and bool(re.search('[^\d]',w.replace('×',''))):
				return True

	return False 


def getMWSynonymsDictFromSignalProfile(dataset_path):
	"""
		input:	dataset_path: a string : directory of saving the test dataset(contains the profile of products)
		output: a dict : {'w1':[w2,w3,...],'w2':[w1,w3,...],'w3':[w1,w2,...],...}
	"""
	result={}
	products={}
	mpnmw_list=[]
	#get all the mpn
	for source in os.listdir(dataset_path)[:]:
		for specification in os.listdir(os.path.join(dataset_path, source))[:]:
			specification_number = specification.replace('.json', '')
			specification_id = '{}//{}'.format(source, specification_number)
			with open(dataset_path+'/'+source+'/'+specification,encoding='utf-8') as specification_file:
				product=json.load(specification_file)
				for k,v in product.items():
					product[k]=lower(v)
				for k,v in product.items():
					k=k.lower()
					if 'mpn' in k or 'upc' in k:
						mpn_list=[]
						#split value to mpn_list
						if not isinstance(v,list) and  not '/' in v:
							v.strip(':')
							v=[v]
						elif '/' in v:
							v.strip(':')
							v=v.split('/')

						for vi in v:
							vi.strip()
							vi=prestring(vi)
							if ':' in vi:
								continue
							elif ' ' in vi:
								vi=vi.split(' ')
								mpn_list.extend(vi)
							else:
								mpn_list.append(vi)
						#get all the model words in mpnmw_list
						for vi in mpn_list:
							if ismodelword(vi):
								mpnmw_list.append(vi)
	#get all the profile in dataset
	for source in os.listdir(dataset_path)[:]:
		for specification in os.listdir(os.path.join(dataset_path, source))[:]:
			specification_number = specification.replace('.json', '')
			specification_id = '{}//{}'.format(source, specification_number)
			with open(dataset_path+'/'+source+'/'+specification,encoding='utf-8') as specification_file:
				product=json.load(specification_file)
				title=product['<page title>'].lower()
				syns='-,;"\'、!@#$%^()[]+~*|&/\\'
				for syn in list(syns):
					title=title.replace(syn,' ')
				del product['<page title>']
				for k,v in product.items():
					product[k]=lower(v)
				product['<page title>']=title
				if product:
					products[specification_id]=product
				#operate one product profile	
				for k,v in product.items():
					k=k.lower()
					if 'model' in k or k in ['mfr part number','part','part number','manufacturer']:
						v_list=[]
						#split value to v_list
						if not isinstance(v,list) and  not '/' in v:
							v.strip(':')
							v=[v]
						elif '/' in v:
							v.strip(':')
							v=v.split('/')
						for vi in v:
							vi.strip()
							vi=prestring(vi)
							if ':' in vi:
								continue
							elif ' ' in vi:
								vi=vi.split(' ')
								v_list.extend(vi)
							else:
								v_list.append(vi)
						#spliting title save into v_list
						t_list=title.split(' ')
						for vi in t_list:
							if ismodelword(vi):
								v_list.append(vi)
								break
						#get all the model words in v_list
						vmw_list=[]
						for vi in v_list:
							if ismodelword(vi) and vi not in mpnmw_list:
								vmw_list.append(vi)
						#save into result
						for token in vmw_list:
							if token in result:
								result[token].extend(vmw_list)
							else:
								result[token]=vmw_list
							ret=list(set(result[token]))
							while token in ret:
								ret.remove(token)
							if len(ret)>0:
								result[token]=ret
							if len(ret)==0 and token in result: 
								del result[token]
								continue
							#result[token].append(token)
							result[token]=list(set(result[token]))							
	return result


def getMWSynoDictFromData(dataset_path):
	result = getMWSynonymsDictFromSignalProfile(dataset_path)
	resultjs = json.dumps(result)
	f=open('./MWSynonymsDict_s.json','w',encoding='utf-8')
	f.write(resultjs)
	f.close()
	##print result
	#for kk,vv in result.items():
	#	print(kk,vv)
	#print(len(result))


if __name__ == '__main__':
	dataset_path='../../DI2KG_Datasets/X-monitor_specs/2013_monitor_specs'
	getMWSynoDictFromData(dataset_path)

	print("\nThe model word synonym dictionary was successfully obtained from the data set!")
	print("The synonym dictionary was written into MWSynonymsDict_s.json")