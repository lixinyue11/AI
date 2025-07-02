import numpy as np
import faiss
from sklearn.preprocessing import normalize
from sentence_transformers import SentenceTransformer

# 初始化模型

model = SentenceTransformer('all-MiniLM-L6-v2')

# 示例文档
documents = [
    "RAG 是一种检索增强生成方法。",
    "向量检索的目标是寻找语义相似的文档。",
    "深度学习模型的训练通常需要大量的数据。",
    "自然语言处理在现代 AI 中非常重要。"
]

# 1. 将文本转化为嵌入向量（embedding）
doc_embeddings = model.encode(documents)

# 2. 将向量进行归一化处理（使其适应余弦相似度检索）
doc_embeddings = normalize(doc_embeddings)

# 3. 创建 FAISS 索引（L2距离即欧式距离，FAISS 默认使用内积实现余弦相似度）
index = faiss.IndexFlatIP(doc_embeddings.shape[1])  # IP = 内积（用于计算余弦相似度）
index.add(doc_embeddings)  # 将文档向量添加到索引中

# 4. 对用户查询进行向量化
query = "什么是向量检索？"
query_vector = model.encode([query])

# 5. 同样归一化查询向量
query_vector = normalize(query_vector)

# 6. 使用 FAISS 检索最相似的文档（返回 top 2）
D, I = index.search(query_vector, k=2)

# 输出结果
print(f"查询: {query}")
print("检索到的相关文档:")
for i in I[0]:
    print(f"- {documents[i]}")
