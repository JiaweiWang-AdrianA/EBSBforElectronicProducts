import os
import csv
from similarity import *
from transformer import *
from measure import *
from tqdm import tqdm

if __name__ == '__main__':
	dataset_path='../DI2KG_Datasets/Y'
	products={}
	for source in tqdm(sorted(os.listdir(dataset_path))):
		if '.DS' in source: #ignore the hidden files
				continue
		for specification in sorted(os.listdir(os.path.join(dataset_path, source))):
			specification_number = specification.replace('.json', '')
			specification_id = '{}//{}'.format(source, specification_number)
			filepath = os.path.join(dataset_path, source, specification_number+'.json')
			if '.DS' in filepath: #ignore the hidden files
				continue
			with open(filepath, encoding='utf-8') as specification_file:
				product=json.load(specification_file)
				
				#lower
				title=product['<page title>'].lower()
				del product['<page title>']
				for k,v in product.items():
					product[k]=lower(v)
				product['<page title>']=title
				if product:
					products[specification_id]=product
	print('>>> dataset read successfully!\n')
	
	#match the brand
	brands,pds_with_bds,pds_without_bds,bds=MatchBrand(products)
	pds_with_bds['unknown']=pds_without_bds

	#process each brand class  
	results=[]
	for brand in tqdm(sorted(list(pds_with_bds.keys()))):
		product=pds_with_bds[brand]
		
		if len(product.keys())<2:
			continue

		#preprocess
		new_product={}
		for k,v in product.items():
			np=pre_process(k,v,brand)
			if np:
				new_product[k]=np
		product=new_product
					
		#block scheme 1 for title source
		block_scheme1=Block_Scheme(product,'t','mw',1)
		#print('block_scheme1 num:',len(block_scheme1))

		#block scheme 2 for description source
		block_scheme2=Block_Scheme(product,'d','mw',1)
		#print('block_scheme2 num:',len(block_scheme2))

		#block scheme aggregator
		blocks=Aggregator('x',block_scheme1,block_scheme2)
		#print('blocks num:',len(blocks))

		#clustering
		product_set=Clustering(product,blocks)

		#add record
		for cluster in sorted(list(product_set.values())):
			if len(cluster)<2:
				continue
			for pair in itertools.combinations(cluster,2):
				id_a,id_b=pair
				results.append((id_a,id_b))

	#write to file			
	headers=['left_spec_id','right_spec_id']
	with open('./result/submission.csv','w',newline='') as f:
		f_csv = csv.writer(f)
		f_csv.writerow(headers)
		f_csv.writerows(results)

	#measure the result
	fsize = os.path.getsize('./result/submission.csv')
	fsize = fsize/float(1024)
	print('file size:',fsize)
	P,R,f1_measure=measure('./result/submission.csv')
	print(P,R,f1_measure)
	with open('./result/measureResult.txt','a+') as f:
		f.write('P:%.4f R:%.4f F:%.4f\n'%(P,R,f1_measure))