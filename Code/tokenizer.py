import string
import Levenshtein
from preprocess import *

def clean(text):
	"""clean the text"""
	if isinstance(text,list):
		texts=[]
		for t in text:
			t=clean(t)
			if t:
				texts.append(t)
		return texts
	elif isinstance(text,str):
		punctuation=""
		text = ''.join(c for c in text if c not in string.punctuation).strip()
		return text.lower()
	else:
		print('clean error')

def MW_Tokenizer(source):
	"""extract model words from source
	   input: an source(title/description),
	   output: the model words of this profile"""
	model_word=[]
	numpattern = re.compile('[0-9]+')
	for string in source:
		temstr = string.split(' ')
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

def Text_Tokenizer(source,tokenizer_type='wo'):
	"""tokenizer the source"""
	if source:
		new_source=[]
		source_process(source,new_source)
		
		if tokenizer_type=='mw':
			return MW_Tokenizer(new_source)
	else:
		return []
