from tokenizer import *
import itertools

def Transfer(tokens,k):
	"""
		input:a list(the values of profile_Tokenizer()) & an integer($transfer)
		output:a list of block's key words
	"""
	result=[]
	if tokens:
		if(len(tokens)>=k):
			for i in itertools.combinations(tokens, k):
				i=list(i)
				i.sort()
				result.append(tuple(i))
	return sorted(result)

def Block_Scheme(dataset,source_type,tokenizer,transfer):
	"""
		input:	dataset ;
				source_type : "t" / "d" ;
				tokenizer : "wo" / "mw" / "sx" / "3q" ;
				transfer : integer k
		output:	a dictionary : key-value: ('word1','word2',...,'wordk'):"product_id1,product_id2,..."
	"""
	blocks={}
	if dataset:
		for product_id,profile in sorted(dataset.items(), key=lambda x: x[0]):
			if source_type=="t":#title
				title=profile.get("<page title>")
				temblocks=Transfer(Text_Tokenizer(title,tokenizer),transfer)
				
			elif source_type=="d":#description
				dict_d=dict(profile)
				if "<page title>" in dict_d:
					del dict_d["<page title>"]
				description=list(dict_d.values())
				temblocks=Transfer(Text_Tokenizer(description,tokenizer),transfer)

			for block in sorted(temblocks):
				if block not in blocks:
					blocks[block]=[product_id]
				else:
					blocks[block].append(product_id)
	
	new_blocks={}
	for k in list(blocks.keys()):
		if len(blocks[k])>=2:
			new_blocks[k]=','.join(sorted(blocks[k]))
	del blocks
	return new_blocks

def Aggregator(operator,block_scheme1,block_scheme2):
	"""
		input:	operator: "+"(union) / "x"(conjunction) ;
				block_scheme: a dictionary (the output of Block_Scheme)
		output:	a dictionary(new block_scheme)
	"""
	blocks={}
	if block_scheme1 or block_scheme2:
		if operator=="+":
			blocks=block_scheme1
			for bwords,bproducts in sorted(block_scheme2.items(), key=lambda x: x[0]):
				if bwords not in blocks:
					blocks[bwords]=bproducts
				else:
					for product in bproducts.split(','):
						if product not in blocks[bwords].split(','):
							blocks[bwords]+=','+product

		elif operator=="x":
			temblocks=Aggregator("+",block_scheme1,block_scheme2)
			
			reverseblocks={}
			for bwords,bproducts in sorted(temblocks.items(), key=lambda x: x[0]):
				if bproducts not in reverseblocks:
					reverseblocks[bproducts]=list(bwords)
				else:
					for word in bwords:
						if word not in reverseblocks[bproducts]:
							reverseblocks[bproducts].append(word)
			
			for bproducts,bwords in sorted(reverseblocks.items(), key=lambda x: x):
				blocks[tuple(sorted(bwords))]=bproducts

			new_blocks={}
			for bword,bproducts in sorted(blocks.items(), key=lambda x: x[0]):
				s1=set(bproducts.split(','))
				is_sub=False
				for product in sorted(list(new_blocks.values())):
					if s1.issubset(set(product.split(','))):
						is_sub=True
						break
				if not is_sub:
					new_blocks[bword]=bproducts
			blocks=new_blocks
	for bwords in list(blocks.keys()):
		blocks[bwords]=','.join(sorted(blocks[bwords].split(',')))
			
	return blocks
