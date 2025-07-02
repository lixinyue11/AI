# 加载文本文件
import os

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
file_path='文件夹路径'
loader = TextLoader(file_path, encoding='utf-8')
docs = loader.load()

# 根据 { 符号进行文本切块
text_splitter = CharacterTextSplitter(separator='{', keep_separator=True)
chunks = text_splitter.split_documents(docs)
# 创建向量存储




embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key=os.getenv("API的KEY")
)
vector = FAISS.from_documents(
            documents=chunks,  # 设置保存的文档
            embedding=embeddings  # 设置 embedding model
        )
# 向量检索相关文档
retriever = vector.as_retriever()
# 将多个问题合起来生成总结性问题

relevant_docs = retriever.invoke('提示词')##添加提示词

if relevant_docs:
    # 取向量检索相关度第一的材料信息
    top_vector_doc = relevant_docs[0].page_content
else:
    top_vector_doc = "No relevant context found by vector retrieval."
