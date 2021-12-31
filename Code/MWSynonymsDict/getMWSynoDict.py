import json
import csv
import os

def getResultList(dataset_paths):
	resultlist=[]
	for path in dataset_paths:
		with open(path) as keyspart_file:
			resultlist.append(json.load(keyspart_file))
	return resultlist

def getMWSynoDict(filepath,keyspart_filename,rest_filenames):
	"""
		input: some synonym dictionary json file
		output: one synonym dictionary json file
	"""
	dataset_paths=[]
	#keyspart_filename='MWSynonymsDict_'
	for i in rest_filenames:
		path=filepath+keyspart_filename+str(i)+'.json'
		dataset_paths.append(path)
	resultlist=getResultList(dataset_paths)

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
	#print(result)
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
	f=open('./MWSynonymsDict.json','w',encoding='utf-8')
	f.write(resultjs)
	f.close()


if __name__ == '__main__':
	filepath = './'
	keyspart_filename = 'MWSynonymsDict_'
	rest_filenames = ['s','m']
	getMWSynoDict(filepath,keyspart_filename, rest_filenames)
	print("\nThese model word synonym dictionaries were successfully summarized into one dictionary!")
	print("The synonym dictionary was written into MWSynonymsDict.json")