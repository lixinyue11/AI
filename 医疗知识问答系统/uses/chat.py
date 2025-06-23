import json
import os
import re
from concurrent.futures.thread import ThreadPoolExecutor

import faiss
import numpy as np
from openai import OpenAI
from .ReasoningRAG_root import ReasoningRAG
from .config import Config
from .knowlage_datasets import clean_text
from .retrievor import q_searching
from .vector_split import vectorize_query
# 创建默认知识库目录
KB_BASE_DIR = Config.kb_base_dir
DEFAULT_KB = Config.default_kb
DEFAULT_KB_DIR = os.path.join(KB_BASE_DIR, DEFAULT_KB)
os.makedirs(DEFAULT_KB_DIR, exist_ok=True)
client_openai = OpenAI(
    api_key=Config.llm_api_key,
    base_url=Config.llm_base_url
)
def get_kb_paths(kb_name: str) :
    """获取指定知识库的索引文件路径"""
    kb_dir = os.path.join(KB_BASE_DIR, kb_name)
    return {
        "index_path": os.path.join(kb_dir, "semantic_chunk.index"),
        "metadata_path": os.path.join(kb_dir, "semantic_chunk_metadata.json")
    }
###向量搜索



def vector_search(query, index_path, metadata_path, limit):#####对向量做索引搜查
    """基本向量搜索函数"""
    print(query)
    query_vector= vectorize_query(query)
    if query_vector.size == 0: return []
    query_vector=np.array(query_vector,dtype=np.float32).reshape(1,-1)

    index=faiss.read_index(index_path)
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except UnicodeDecodeError:
        print(f"警告：{metadata_path} 包含非法字符，使用 UTF-8 忽略错误重新加载")
        with open(metadata_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
            metadata = json.loads(content)
    D, I = index.search(query_vector, limit)##faiss查询
    results = [metadata[i] for i in I[0] if i < len(metadata)]##和json对应取出
    return results

def get_search_background(query: str, max_length: int = 1500) -> str:
    try:

        search_results = q_searching(query)
        cleaned_results = re.sub(r'\s+', ' ', search_results).strip()
        return cleaned_results[:max_length]
    except Exception as e:
        print(f"联网搜索失败：{str(e)}")
        return ""
class DeepSeekClient:
    def generate_answer(self, system_prompt, user_prompt, model=Config.llm_model):
        response = client_openai.chat.completions.create(
            model=Config.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content.strip()
def generate_answer_from_deepseek(question: str, system_prompt: str = "你是专业的问答，请根据背景知识回答问题。", background_info= None) -> str:
    deepseek_client = DeepSeekClient()
    user_prompt = f"问题：{question}"
    if background_info:
        user_prompt = f"背景知识：{background_info}\n\n{user_prompt}"
    try:
        answer = deepseek_client.generate_answer(system_prompt, user_prompt)
        return answer
    except Exception as e:
        return f"生成回答时出错：{str(e)}"
####输入，选择知识库，启用联网搜索，启用表格格式化，启用多跳，聊天历史
def process_question_with_reasoning(question: str, kb_name: str = DEFAULT_KB, use_search: bool = True, use_table_format: bool = False, multi_hop: bool = False, chat_history = None):
    """增强版process_question，支持流式响应，实时显示检索和推理过程，支持多知识库和对话历史"""
    kb_paths = get_kb_paths(kb_name)
    index_path = kb_paths["index_path"]
    metadata_path = kb_paths["metadata_path"]
    # 构建带对话历史的问题
    if chat_history and len(chat_history)>0:
        context="之前的对话内容：\n"
        for user_msg,assistant_msg in chat_history[-3:]:
            context += f"用户：{user_msg}\n"
            context += f"助手：{assistant_msg}\n"
        context += f"\n当前问题：{question}"
        enhanced_question = f"基于以下对话历史，回答用户的当前问题。\n{context}"
    else:enhanced_question = question

    print("-------",enhanced_question)

    # 初始状态
    search_result = "联网搜索进行中..." if use_search else "未启用联网搜索"
    '''多跳'''
    if multi_hop:
        reasoning_status = f"正在准备对知识库 '{kb_name}' 进行多跳推理检索..."
        search_display = f"### 联网搜索结果\n{search_result}\n\n### 推理状态\n{reasoning_status}"
        yield search_display, "正在启动多跳推理流程..."
    else:
        reasoning_status = f"正在准备对知识库 '{kb_name}' 进行向量检索..."
        search_display = f"### 联网搜索结果\n{search_result}\n\n### 检索状态\n{reasoning_status}"
        yield search_display, "正在启动简单检索流程..."

    search_future = None
    with ThreadPoolExecutor(max_workers=1) as executor:
        if use_search:
            search_future = executor.submit(get_search_background, question)
    # 检查索引是否存在
    print('='*50)
    print(index_path,metadata_path)
    '''基本用不上，上传文件之后会形成索引和文本的切割'''
    # if not (os.path.exists(index_path) and os.path.exists(metadata_path)):
    #     print('不存在下标，但是存在文本切割')
    #     if search_future:
    #         # 等待搜索结果
    #         search_result = "等待联网搜索结果..."
    #         search_display = f"### 联网搜索结果\n{search_result}\n\n### 检索状态\n知识库 '{kb_name}' 中未找到索引"
    #         yield search_display, "等待联网搜索结果..."
    #
    #         search_result = search_future.result() or "未找到相关网络信息"
    #         system_prompt = "你是一名问答专家。请考虑对话历史并回答用户的问题。"
    #         if use_table_format:
    #             system_prompt += "请尽可能以Markdown表格的形式呈现结构化信息。"
    #         answer = generate_answer_from_deepseek(enhanced_question, system_prompt=system_prompt,
    #                                                background_info=f"[联网搜索结果]：{search_result}")
    #
    #         search_display = f"### 联网搜索结果\n{search_result}\n\n### 检索状态\n无法在知识库 '{kb_name}' 中进行本地检索（未找到索引）"
    #         yield search_display, answer
    #     else:
    #         yield f"知识库 '{kb_name}' 中未找到索引，且未启用联网搜索", "无法回答您的问题。请先上传文件到该知识库或启用联网搜索。"
    #     return

    '''多跳'''
    if multi_hop:
        # 使用多跳推理的流式接口
        reasoning_rag = ReasoningRAG(
            index_path=index_path,
            metadata_path=metadata_path,
            max_hops=3,
            initial_candidates=5,
            refined_candidates=3,
            verbose=True
        )
        for step_result in reasoning_rag.stream_retrieve_and_answer(enhanced_question, use_table_format):
            # 更新当前状态
            status = step_result["status"]
            reasoning_display = step_result["reasoning_display"]
            # 如果有新的答案，更新
            if step_result["answer"]:
                current_answer = step_result["answer"]
                # 如果搜索结果已返回，更新搜索结果
            if search_future and search_future.done():
                search_result = search_future.result() or "未找到相关网络信息"
            # 构建并返回当前状态
            current_display = f"### 联网搜索结果\n{search_result}\n\n### 知识库: {kb_name}\n### 推理状态\n{status}\n\n{reasoning_display}"
            yield current_display, current_answer
    '''简单向量搜索，使用enhanced_question'''
    # 执行简单向量搜索，使用enhanced_question
    search_results = vector_search(enhanced_question, index_path, metadata_path, limit=5)##搜索查询
    print('***********')
    if not search_results:
        print(1)
        yield f"### 联网搜索结果\n{search_result}\n\n### 知识库: {kb_name}\n### 检索状态\n未找到相关信息", f"知识库 '{kb_name}' 中未找到相关信息。"
        current_answer = f"知识库 '{kb_name}' 中未找到相关信息。"
    else:
        chunks_detail = "\n\n".join(
            [f"**相关信息 {i + 1}**:\n{result['chunk']}" for i, result in enumerate(search_results[:5])])
        chunks_preview = "\n".join([f"- {result['chunk'][:100]}..." for i, result in enumerate(search_results[:3])])
        #yield f"### 联网搜索结果\n{search_result}\n\n### 知识库: {kb_name}\n### 检索状态\n找到 {len(search_results)} 个相关信息块\n\n### 检索到的信息预览\n{chunks_preview}", "正在生成答案..."

        # 生成答案
        background_chunks = "\n\n".join([f"[相关信息 {i + 1}]: {result['chunk']}"
                                         for i, result in enumerate(search_results)])


        ###模型系统的prompt
        system_prompt='''
        你是资料整理专家。基于提供的背景信息和历史的对话信息，回复用户的问题
        '''
        if use_table_format: system_prompt += "请尽可能以Markdown表格的形式呈现结构化信息。"
        user_prompt=f'''
        {enhanced_question}背景信息：{background_chunks}基于以上的背景信息和对话的历史回答用户的问题,只回答用户问题，不额外输出其他内容。
        '''

        response = client_openai.chat.completions.create(
            model=Config.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        current_answer = response.choices[0].message.content.strip()
        yield f'''###联网搜索结果\n{search_result}\n\n### 知识库: {kb_name}\n### 检索状态\n检索完成，已生成答案\n\n### 检索到的内容\n{chunks_detail}"''', current_answer

        """互联网搜索可以考虑合并"""
        # 检索完成后，如果有搜索结果，可以考虑合并知识
        if search_future and search_future.done():
            search_result = search_future.result() or "未找到相关网络信息"
            # 如果同时有搜索结果和本地检索结果，可以考虑合并
            if search_result and current_answer and current_answer not in ["正在分析您的问题...",
                                                                           "本地知识库中未找到相关信息。"]:
                status_text = "正在合并联网搜索和知识库结果..."
                if multi_hop:
                    yield f"### 联网搜索结果\n{search_result}\n\n### 知识库: {kb_name}\n### 推理状态\n{status_text}", current_answer
                else:
                    yield f"### 联网搜索结果\n{search_result}\n\n### 知识库: {kb_name}\n### 检索状态\n{status_text}", current_answer

                # 合并结果
                system_prompt = "你是一名聊天专家，请整合网络搜索和本地知识库提供全面的解答。请考虑对话历史。"

                if use_table_format:
                    system_prompt += "请尽可能以Markdown表格的形式呈现结构化信息。"

                user_prompt = f"""
                               {enhanced_question}

                               网络搜索结果：{search_result}

                               本地知识库分析：{current_answer}

                               请根据以上信息和对话历史，提供一个综合的回答。确保使用Markdown表格来呈现适合表格形式的信息。
                               """
                response = client_openai.chat.completions.create(
                    model="qwen-plus",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                combined_answer = response.choices[0].message.content.strip()
                final_status = "已整合联网和知识库结果"
                if multi_hop:
                    final_display = f"### 联网搜索结果\n{search_result}\n\n### 知识库: {kb_name}\n### 本地知识库分析\n已完成多跳推理分析，检索到的内容已在上方显示\n\n### 综合分析\n{final_status}"
                else:
                    # 获取之前检索到的内容
                    chunks_info = "".join(
                        [part.split("### 检索到的内容\n")[-1] if "### 检索到的内容\n" in part else "" for part in
                         search_display.split("### 联网搜索结果")])
                    if not chunks_info.strip():
                        chunks_info = "检索内容已在上方显示"
                    final_display = f"### 联网搜索结果\n{search_result}\n\n### 知识库: {kb_name}\n### 本地知识库分析\n已完成向量检索分析\n\n### 检索到的内容\n{chunks_info}\n\n### 综合分析\n{final_status}"

                yield final_display, combined_answer


    # 检索完成后，如果有搜索结果，可以考虑合并知识



