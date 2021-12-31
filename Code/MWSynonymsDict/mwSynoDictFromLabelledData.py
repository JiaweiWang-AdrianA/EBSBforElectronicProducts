import json
import csv
import os
import re
from string import digits	
from mwSynoDictFromData import *


def prestring(string):
	string=string.replace('|',' ')
	string=string.replace('(',' ')
	string=string.replace(')',' ')
	string=string.replace(',',' ')
	string=string.replace('"',' ')
	string=string.replace('\'',' ')
	string=string.replace('\n',' ')
	string=string.replace('\t',' ')
	while '  ' in string:
		string=string.replace('  ',' ')
	return string


def Get_LabelledDataset(labelled_dataset_path):
	labelled_dataset=[]
	with open(labelled_dataset_path) as lbds_file:
		lbds_file_csv=csv.reader(lbds_file)
		for row in lbds_file_csv:
			if row[2]=='1':
				labelled_dataset.append([row[0],row[1]])
	return labelled_dataset

def source_process(source,new_source):
	"""process the source"""
	if isinstance(source,list):
		for s in source:
			source_process(s,new_source)
	elif isinstance(source,str):
		if source and source.strip()!='' and source not in new_source:
			new_source.append(source)

def ismodelword(w):
	if len(w)<4:
		return False
	if w in ['3m','3d','720p','1080p','2711p','1920x1080','rs-232','ohc24','2xhdmi']:
		return False
	for word in ['720p','1080p','2711p']:
		if word in w:
			return False

	endwords=['.com','.ca','slr','cm','mm','ms','mp','megapixel','display','in','inch','hz','bit','cd','cc','year','years']
	for word in endwords:
		partlen=0-len(word)
		if w[partlen:]==word and (len(w)-len(word)<5 or is_number(w[:partlen])):
			return False
	#startwords=['lcd-','ctr-','led-','tft-','megapixel','ohc','rs','win']
	startwords=['lcd','ctr','led','tft','megapixel','ohc','rs','win']
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
	if len("".join(filter(str.isdigit, w)))>0 and len(w.translate(str.maketrans('', '', digits)))>0:
		match_string=re.search(numpattern, w)
		if match_string:
			if bool(re.search('[^\d]',w.replace('.',''))) and bool(re.search('[^\d]',w.replace(',',''))) and bool(re.search('[^\d]',w.replace('×',''))):
				return True

	return False 


def matchedkeys(key1,P2):
	key1list=key1.split(' ')
	rek=-1
	for key2 in P2.keys():
		if key2 == key1:
			rek=key2
			break
		if key2 in ['mfr part number','part','part number','manufacturer'] and key1 in ['mfr part number','part','part number','manufacturer']:
			rek=key2
		if 'description' in key2 and 'description' in key1:
			rek=key2
		if 'product' in key2 and 'product' in key1:
			rek=key2
		if 'model' in key2 and 'model' in key1:
			rek=key2
	return rek
	

def get_matchedmodelwords(P1,P2):
	result={}
	vmw_list=[]
	if len(P1)>len(P2):
		P1,P2=P2,P1

	title1=P1['<page title>']
	title2=P2['<page title>']
	t_list1=title1.split(' ')
	t_list2=title2.split(' ')
	for t_list in [t_list1,t_list2]:
		for vi in t_list:
			vi=prestring(vi)
			if ismodelword(vi):
				vmw_list.append(vi)
				break			

	for k1,v1 in P1.items():
		if 'model' not in k1 and k1 not in ['mfr part number','part','part number','manufacturer','product name','description','product description']:
			continue
		key2=matchedkeys(k1,P2)
		if key2==-1:
			continue
		v2=P2[key2]
		#split v1,v2 to v_list
		v_list=[]
		for v in [v1,v2]:
			if not isinstance(v1,list) and  not '/' in v:
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
		#get all the model words in v_list
		for vi in v_list:
			if ismodelword(vi):
				vmw_list.append(vi)
		#print(k1,vmw_list)
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


def getMWSynoDictFromLabelledData(labelled_dataset_path,dataset_path):
	#get the labelled dataset
	resultlist=[]
	count=0
	labelled_dataset=Get_LabelledDataset(labelled_dataset_path)

	for match_profile_ids in labelled_dataset:
		count+=1
		match_profile=[]
		for profile_id in match_profile_ids:
			profile_path=profile_id.replace('//','/')+'.json'
			with open(dataset_path+'/'+profile_path) as specification_file:
				product=json.load(specification_file)
				#preprocess title
				title=product['<page title>'].lower()
				syns='-,;"\'、!@#$%^()[]+~*|&/\\'
				for syn in list(syns):
					title=title.replace(syn,' ')
				product['<page title>']=title
				for k,v in product.items():
					product[k]=lower(v)
				match_profile.append(product)
		i=0
		for profile in match_profile:
			for kk,vv in profile.items():
				if isinstance(vv,list):
					newvv=[]
					source_process(vv,newvv)
					profile[kk]=' '.join(newvv)
			match_profile[i]=profile
			i+=1
		resultlist.append(get_matchedmodelwords(match_profile[0],match_profile[1]))

	temresult={}
	for keydict in resultlist:
		for key in keydict:
			if key in temresult:
				temresult[key].extend(keydict[key])
				temresult[key]=list(set(temresult[key]))
			else:
				temresult[key]=keydict[key]

	result={}
	result.update(temresult)

	for key in temresult:
		for keyc in temresult[key]:
			if keyc in result:
				result[key].extend(result[keyc])
				result[key]=list(set(result[key]))
		if key in result[key]:
			result[key].remove(key)

		temkeys=[key]
		temkeys.extend(result[key])
		temresult2={}
		temresult2.update(result)
		for keyc in temresult2[key]:
			if keyc in result: del result[keyc]
			result[keyc]=list(temkeys)
			result[keyc].remove(keyc)
			result[keyc]=list(set(result[keyc]))
			
	resultjs = json.dumps(result)
	f=open('./MWSynonymsDict_m.json','w',encoding='utf-8')
	f.write(resultjs)
	f.close()
	##print result
	#for kk,vv in result.items():
	#	print(kk,vv)
	#print(len(result))


if __name__ == '__main__':
	labelled_dataset_path = '../../DI2KG_Datasets/YER-monitor_entity_resolution_labelled_data.csv'
	dataset_path = '../../DI2KG_Datasets/Y'
	getMWSynoDictFromLabelledData(labelled_dataset_path,dataset_path)
	print("\nThe model word synonym dictionary was successfully obtained from the labelled data set!")
	print("The synonym dictionary was written into MWSynonymsDict_m.json")
