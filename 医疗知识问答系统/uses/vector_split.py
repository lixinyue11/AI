import json
import re
import traceback

import faiss
import numpy as np
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core.node_parser import SentenceSplitter
from openai import OpenAI


from 大模型.RAG.Advanced_product.RagHop.rag import clean_text
from .config import Config
def read_json(file_path):
    jaon_read=json.load(open(file_path,encoding='utf-8'))
    reslut=[]
    for i in jaon_read:
        reslut.append(i)
    print(reslut)
    return reslut
def write_json(datasets,file):
    with open(file, 'w', encoding='utf-8') as outfile:
        json.dump(datasets, outfile, ensure_ascii=False, indent=4)

def semantic_chunk(text,chunk_size=800,chunk_overlap=20,name=''):
    '''对源文本进行处理每一句需要达到chunk_size'''
    '''
    通过标点符号 进行分割
    
    class EnhancedSentenceSplitter(SentenceSplitter):
    def __init__(self, *args, **kwargs):
        custom_seps = ["；", "!", "?", "\n"]
        separators = [kwargs.get("separator", "。")] + custom_seps
        kwargs["separator"] = '|'.join(map(re.escape, separators))
        super().__init__(*args, **kwargs)

    def _split_text(self, text: str, **kwargs) -> typing.List[str]:
        splits = re.split(f'({self.separator})', text)
        chunks = []
        current_chunk = []
        for part in splits:
            part = part.strip()
            if not part:
                continue
            if re.fullmatch(self.separator, part):
                if current_chunk:
                    chunks.append("".join(current_chunk))
                    current_chunk = []
            else:
                current_chunk.append(part)
        if current_chunk:
            chunks.append("".join(current_chunk))
        return [chunk.strip() for chunk in chunks if chunk.strip()]

# 创建 EnhancedSentenceSplitter 实例
text_splitter = EnhancedSentenceSplitter(
    separator="。",
    chunk_size=800,
    chunk_overlap=200,
    paragraph_separator="\n\n"
)

    
    '''
    paragraphs = []
    current_para = []
    current_len = 0
    for para in text.split("\n\n"):
        para = para.strip()
        para_len = len(para)

        if para_len == 0:
            continue
        if current_len + para_len <= 50:
            current_para.append(para)
            current_len += para_len
        else:
            paragraphs.append(para)
            current_len = para_len
    datass = current_para + paragraphs
    if datass:
        datass.append("\n".join(current_para))
    '''文件进行分块处理'''
    chunk_data_list = []
    chunk_id = 0
    text_spliter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    for para in paragraphs:
        chunks  = text_spliter.split_text(para)
        for chunk in chunks:
            if len(chunk) < 20:
                continue
            chunk_data_list.append({
                "id": f'chunk{chunk_id}',
                "chunk": chunk,
                "title": str(name),
                "method": "semantic_chunk"
            })
            chunk_id += 1
    print(chunk_data_list)
    return chunk_data_list


def vectorize_query(query,batch_size=Config.batch_size,model_name= "text-embedding-v3"):######做成向量文件
    embedding_client = OpenAI(
        api_key=Config.api_key,
        base_url=Config.base_url
    )
    if isinstance(query, str):
        query = [query]

    # 分批处理有效查询
    all_vectors = []
    valid_queries = []
    for q in query:
        clean_q = clean_text(q)
        valid_queries.append(clean_q)
    for i in  range(0,len(valid_queries),batch_size):
        batch = valid_queries[i:i + batch_size]
        completion = embedding_client.embeddings.create(
            model=model_name,
            input=batch,
            dimensions=Config.dimensions,
            encoding_format="float"
        )

        vectors = [embedding.embedding for embedding in completion.data]
        all_vectors.extend(vectors)

    return np.array(all_vectors)

def vectorize_file(data_list,output_file_path,field_name='chunk',name=''):
    """向量化文件内容，处理长度限制并确保输入有效"""
    print(output_file_path)
    if not data_list:
        print("警告: 没有数据需要向量化")
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            json.dump([], outfile, ensure_ascii=False, indent=4)
        return
    # 准备查询文本，确保每个文本有效且长度适中
    valid_data = []
    valid_texts = []



    for data in  data_list:
        text=data.get(field_name,'')

        if text and 1 <= len(text) <= 8000:  # 略小于API限制的8192，留出一些余量
            valid_data.append(data)
            valid_texts.append(text)
        else:
            # 如果文本太长，截断它
            if len(text) > 8000:
                truncated_text = text[:8000]
                print(f"警告: 文本过长，已截断至8000字符。原始长度: {len(text)}")
                data[field_name] = truncated_text
                valid_data.append(data)
                valid_texts.append(truncated_text)
            else:
                print(f"警告: 跳过空文本或长度为0的文本")

    # 向量化有效文本
    vectors = vectorize_query(valid_texts)
    # 检查向量化是否成功
    if vectors.size == 0 or len(vectors) != len(valid_data):
        print(
            f"错误: 向量化失败或向量数量({len(vectors) if vectors.size > 0 else 0})与数据条目({len(valid_data)})不匹配")
        # 保存原始数据，但不含向量
        try:
            reasult_data=read_json(output_file_path)
            write_json(reasult_data+valid_data,output_file_path)
        except:
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                json.dump(valid_data, outfile, ensure_ascii=False, indent=4)
        return
        # 添加向量到数据中
    print(valid_data)
    print(output_file_path)
    for data, vector in zip(valid_data, vectors):
        data['vector'] = vector.tolist()
    try:
        reasult_data = read_json(output_file_path)
        write_json(reasult_data+valid_data, output_file_path)
    except:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(valid_data, outfile, ensure_ascii=False, indent=4)

    print(f"成功向量化 {len(valid_data)} 条数据并保存到 {output_file_path}")


def build_faiss_index(vector_file, index_path, metadata_path,name=''):
    with open(vector_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    valid_data = []
    for item in data:
        if 'vector' in item and item['vector']:
            valid_data.append(item)
    # 提取向量
    vectors = [item['vector'] for item in valid_data]
    vectors = np.array(vectors, dtype=np.float32)

    # 检查向量维度
    dim = vectors.shape[1]
    n_vectors = vectors.shape[0]

    # 确定索引类型和参数
    max_nlist = n_vectors // 39
    nlist = min(max_nlist, 128) if max_nlist >= 1 else 1

    if nlist >= 1 and n_vectors >= nlist * 39:
        quantizer = faiss.IndexFlatIP(dim)
        index = faiss.IndexIVFFlat(quantizer, dim, nlist)
        if not index.is_trained:index.train(vectors)
        index.add(vectors)
    else:
        print(f"使用 IndexFlatIP 索引")
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
    faiss.write_index(index, index_path)
    print(f"成功写入索引到 {index_path}")

    metadata = [{'id': item['id'], 'chunk': item['chunk'], 'method': item['method']} for item in valid_data]
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    print(f"成功写入元数据到 {metadata_path}")

    return True




