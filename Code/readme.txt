【系统入口】entity_resolution.py
【系统功能】
	输入：待判断的产品文件数据集
	输出：所有匹配产品文件对并保存至result/submission.csv；根据标签集对输出结果的测量结果保存至result/measureResult.txt

【子模块功能】
 【/Code/目录下】
  1. preprocess.py：对数据进行预处理，包括数据清除，同义词替换等
  2. tokenizer.py：模型词和关键词的提取模块，属于BA-SA的子模块
  3. transformer.py：BA-SA的主模块，利用提取的模型词和关键词对数据集进行分块和块聚合操作，将每一个文件映射到一个块中
  4. similarity.py：计算每一个块中的任两个产品文件间的相似度，判断是否属于同一实际产品
  5. measure.py：根据标记数据集测量系统得到的结果，计算准确率，召回率和F1值
 【/Code/MWSynonymsDict目录下】
  1. mwSynoDictFromData.py：从数据集中提取模型词同义词字典，并将结果保存至MWSynonymsDict_s.json
  2. mwSynoDictFromLabelledData.py：从标签数据集中提取模型词同义词字典，并将结果保存至MWSynonymsDict_m.json
  3. getMWSynoDict.py：将多个同义词字典转化为一个同义词字典，并将结果保存至MWSynonymsDict.json

【运行方式】
1. 运行实体解析系统：进入Code目录下，直接运行entity_resolution.py
  （默认运行数据集为DI2KG_Datasets/Y，若更改其他数据集，若无准确结果文件则无法进行结果测量，需要手动将entity_resolution.py中的mesure the result部分删除）
2. 运行模型词同义词字典：进入/Code/MWSynonymsDict目录下，先运行mwSynoDictFromData.py和mwSynoDictFromLabelledData.py，再运行getMWSynoDict.py，最终得到的同义词字典文件为MWSynonymsDict.json


