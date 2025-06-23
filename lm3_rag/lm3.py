import os
import requests
import re
import json
from openai import OpenAI
from dotenv import load_dotenv
import torch
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer,util
load_dotenv()
client=OpenAI(base_url='http://127.0.0.1:11434/v1',api_key='llama3:8b')
model=SentenceTransformer('D:\\360Downloads\\HUGGFACE\\sentence-transformers\\all-MiniLM-L6-v2')
#设置颜色
pink='\033[95m'
cyan='\033[96m'
yellow='\033[93m'
neon_green='\033[92m'
reset_color='\033[0m'
def open_file(filepath):
    with open(filepath,'r',encoding='utf-8') as f:
        return f.read()
def get_relevant_context(user_input,vault_embeddings,vault_content,model,tok_k=7):
    if vault_embeddings.nelement()==0:return []
    input_embedding=model.encode([user_input])
    cos_scores=util.cos_sim(input_embedding,vault_embeddings)[0]
    tok_k=min(tok_k,len(cos_scores))
    top_indices=torch.topk(cos_scores,k=tok_k)[1].tolist()
    reslevant_context=[vault_content[idx].strip() for idx in top_indices]
    return reslevant_context
def write_to_motes(note_context):
    with open('notes.txt','a+',encoding='utf-8') as f:f.write(note_context+'\n')