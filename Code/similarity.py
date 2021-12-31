from tokenizer import *

def TitleSim(title_a,title_b): 
	"""computes the similarity between title title_a and title_b"""
	t_a,t_b=Text_Tokenizer(title_a[0],'mw'),Text_Tokenizer(title_b[0],'mw')
	t_a_l,t_b_l=len(t_a),len(t_b)
	sa,sb={},{}
	for s in title_a[1:]:
		ss=Text_Tokenizer(s,'mw')
		for sss in sorted(ss):
			if sss in sa:
				sa[sss]+=1
			else:
				sa[sss]=1
	for s in title_b[1:]:
		ss=Text_Tokenizer(s,'mw')
		for sss in sorted(ss):
			if sss in sb:
				sb[sss]+=1
			else:
				sb[sss]=1
	set_a,set_b=set(),set()
	if sa:
		set_a.add(max(sa, key=sa.get))
	else:
		if t_a_l==0:
			return False
		else:
			set_a.add(t_a[0])
	if sb:
		set_b.add(max(sb, key=sb.get))
	else:
		if t_b_l==0:
			return False
		else:
			set_b.add(t_b[0])
	if t_a_l==1:
		if ((' '+t_a[0].replace('-',' ')+' ') in (' '+title_b[0].replace('-',' ')+' ')):
			return True
		if ((' '+t_a[0].replace('-','')+' ') in (' '+title_b[0].replace('-','')+' ')):
			return True
	if t_b_l==1:
		if ((' '+t_b[0].replace('-',' ')+' ') in (' '+title_a[0].replace('-',' ')+' ')):
			return True
		if ((' '+t_b[0].replace('-','')+' ') in (' '+title_a[0].replace('-','')+' ')):
			return True

	if set_a.issubset(set_b) or set_b.issubset(set_a):
		return True
	else:
		return False
	

#Computes similarity between product descriptions a and b
def ProdSim(a,b):
	"""
		titleSim(title_a,title_b) gives the similarity between title title_a and title_b;
	"""
	# for k in ['model','product model']:
		# if (k in a and a[k] not in ' '.join(list(b.values()))) or (k in b and b[k] not in ' '.join(list(a.values()))):
			# return False
	title_a,title_b=[a.get("<page title>")],[b.get("<page title>")]
	for m in ['mfr part number','part','part number','manufacture','manufacturer','manufacturer part number','mfg model','model','model name','product model','product name','description','product description','description technical detail']:
		if m in a:
			title_a.append(' '.join(a[m]))
		if m in b:
			title_b.append(' '.join(b[m]))
	return TitleSim(title_a,title_b)
			
def Clustering(products,blocks):
	"""
		input:products with the same brand、blocks、similarity level
		output:clusters of different products
	"""
	product_address,product_set,product_comp=dict(),dict(),dict()
	unpsb=set()
	
	cluster_num,unpsb_num=1,0
	for block in sorted(list(blocks.values()),reverse=False):
		block=block.split(',')
		for k1 in range(len(block)):
			product_a_id=block[k1]
			for k2 in range(k1+1,len(block)):
				product_b_id=block[k2]
				if not product_comp.__contains__(product_a_id):
					product_comp[product_a_id]=[]
				if not product_comp.__contains__(product_b_id):
					product_comp[product_b_id]=[]
				if not product_address.__contains__(product_a_id):
					if not product_address.__contains__(product_b_id):
						#product a not belongs to a class,and product b not belongs to a class
						if (product_a_id,product_b_id) in unpsb:
							unpsb_num+=1
							continue
						if ProdSim(products.get(product_a_id),products.get(product_b_id)):
							product_address[product_a_id]=cluster_num
							product_address[product_b_id]=cluster_num
							product_set[cluster_num]=set([product_a_id,product_b_id])
							cluster_num+=1
						else:
							unpsb.add((product_a_id,product_b_id))
					else:
						#product a not belongs to a class,but product b belongs to a class
						if ProdSim(products.get(product_a_id),products.get(product_b_id)):
							product_address[product_a_id]=product_address[product_b_id]
							product_set[product_address[product_b_id]].add(product_a_id)
				else:
					if not product_address.__contains__(product_b_id):
						#product a belongs to a class,but product b not belongs to a class
						if ProdSim(products.get(product_a_id),products.get(product_b_id)):
							product_address[product_b_id]=product_address[product_a_id]
							product_set[product_address[product_a_id]].add(product_b_id)
					else:
						#product a belongs to a class,and product b belongs to another class
						a_address,b_address=product_address[product_a_id],product_address[product_b_id]
						if a_address != b_address:
							if ProdSim(products.get(product_a_id),products.get(product_b_id)):
								for product_id in product_set[b_address]:
									product_address[product_id]=product_address[product_a_id]
								product_set[a_address]=product_set[a_address].union(product_set[b_address])
								del[product_set[b_address]]
								cluster_num+=1
	return product_set
