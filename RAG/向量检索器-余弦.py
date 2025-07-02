###航空公司的手册查询，需要先分词操作
import json
import re

import faiss
import numpy as np
import openai
import requests
from langchain_core.tools import tool
response = requests.get(
    "https://storage.googleapis.com/benchmarks-artifacts/travel-db/swiss_faq.md"
)
response.raise_for_status()
faq_text = response.text
docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
def vectorize_query(valid_queries,oai_client):
    all_vectors=[]
    result_vector=[]
    if isinstance(valid_queries,str):
        valid_queries=[valid_queries]

    for i in range(0, len(valid_queries), 20):
        batch = valid_queries[i:i + 20]
        print(i)
        completion = oai_client.embeddings.create(
            model="text-embedding-3-small",
            input=batch,
           # dimensions=1024,
            #encoding_format="float"
        )
        vectors = [embedding.embedding for embedding in completion.data]
        all_vectors.extend(vectors)
    print(len(valid_queries), len(all_vectors))
    count = 0
    for i, j in zip(valid_queries, all_vectors):
        map_dict = {}
        map_dict['id'] = count
        map_dict['chunk'] = i
        map_dict['vectory'] = j
        count += 1
        result_vector.append(map_dict)
    return result_vector

class VectorStoreRetriever:
    def __init__(self,doc,vectors,oai_client):
        self._arr = np.array(vectors)
        self._docs = docs
        self._client = oai_client
    @classmethod
    def from_docs(cls,docs,oai_client,index_path,metadata_path):
        text_spliter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=300)
        chunks  = text_spliter.split_text(docs)
        chunk_data_list=[]
        all_vectors=[]
        valid_queries=[]
        count=0

        for  text in chunks:
            chunk_data_list.append({'id':count,'chunk':text})
            count+=1
        for i in chunk_data_list:
            valid_queries.append(i['chunk'])

        result_vector=vectorize_query(valid_queries,oai_client)
        ###添加索引
        vectors = [item['vectory'] for item in result_vector]
        vectors = np.array(vectors, dtype=np.float32)
        # 检查向量维度
        dim = vectors.shape[1]
        n_vectors = vectors.shape[0]
        print(dim,n_vectors)
        # 确定索引类型和参数
        max_nlist = n_vectors // 39
        nlist = min(max_nlist, 128) if max_nlist >= 1 else 1

        if nlist >= 1 and n_vectors >= nlist * 39:
            quantizer = faiss.IndexFlatIP(dim)
            index = faiss.IndexIVFFlat(quantizer, dim, nlist)
            if not index.is_trained: index.train(vectors)
            index.add(vectors)
        else:
            print(f"使用 IndexFlatIP 索引")
            index = faiss.IndexFlatIP(dim)
            index.add(vectors)
        faiss.write_index(index, index_path)
        print(f"成功写入索引到 {index_path}")

        metadata = [{'id': item['id'], 'chunk': item['chunk']} for item in result_vector]
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print(f"成功写入元数据到 {metadata_path}")

        return  cls(docs,vectors,oai_client)
    def query(self,query,k=5):
        embed = self._client.embeddings.create(
            model="text-embedding-3-small", input=[query]
        )
        print(self._arr.T)
        scores = np.array(embed.data[0].embedding) @ self._arr.T
        top_k_idx = np.argpartition(scores, -k)[-k:]###最大的数值
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        return [
            {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
        ]

    def query_answer(self,query, index_path, metadata_path, limit):
        query_vector = vectorize_query(query, client_openai)
        query_vector = query_vector[0]['vectory']
        query_vector = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        index = faiss.read_index(index_path)

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except UnicodeDecodeError:
            print(f"警告：{metadata_path} 包含非法字符，使用 UTF-8 忽略错误重新加载")
            with open(metadata_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
                metadata = json.loads(content)
        D, I = index.search(query_vector, limit)  ##faiss查询
        results = [metadata[i] for i in I[0] if i < len(metadata)]  ##和json对应取出
        print('----', results)



llm_api_key = "sk-07b0bbfd24bf4cb391cad5da8da05f6f"  # 与embedding共用同一个key
llm_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 与embedding共用同一个URL
key= "sk-ihk5obdasfaV10econ8bhfUiKroVr8cTnU1C1qJua8VVWygg"
base_urlbase_url="https://poloai.top/v1"
client_openai = OpenAI(
    api_key=key,
    base_url=base_urlbase_url
)
s=''
for i in docs:
    s+=i['page_content']
index_path='D:/User_Pro/faiss/travel_angent/host_answer.index'
metadata_path='D:/User_Pro/faiss/travel_angent/host_answer.json'
retriever = VectorStoreRetriever.from_docs(s, client_openai,index_path,metadata_path)
query='How can I change my reservation?'
docs = retriever.query(query, k=2)
print(docs)