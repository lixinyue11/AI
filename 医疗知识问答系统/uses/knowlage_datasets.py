import json
import os
import re
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from .vector_split import *
import chardet
import fitz

from 大模型.RAG.Advanced_product.医疗知识问答系统.uses.config import Config

KB_BASE_DIR=Config.kb_base_dir
os.makedirs(KB_BASE_DIR, exist_ok=True)

DEFAULT_KB = Config.default_kb
DEFAULT_KB_DIR = os.path.join(KB_BASE_DIR, DEFAULT_KB)
os.makedirs(DEFAULT_KB_DIR, exist_ok=True)


# 创建临时输出目录
OUTPUT_DIR = Config.output_dir
os.makedirs(OUTPUT_DIR, exist_ok=True)
def clean_text(text):
    """清理文本中的非法字符，控制文本长度"""
    if not text:
        return ""
    # 移除控制字符，保留换行和制表符
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # 移除重复的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 确保文本长度在合理范围内
    return text.strip()

def extract_text_from_pdf(file_path):#pdf
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            page_text = page.get_text()
            text += page_text.encode('utf-8', errors='ignore').decode('utf-8')
        if not text.strip():
            print(f"警告：PDF文件 {file_path} 提取内容为空")
        return text
    except Exception as e:
        print(f"PDF文本提取失败：{str(e)}")
        return ""

def  process_upload_to_kb(file_path):
    try:
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            if not text:
                return f"PDF文件 {file_path} 内容为空或无法提取"
        else:
            with open(file_path, "rb") as f:
                content = f.read()
            result=chardet.detect(content)
            detected_encoding = result['encoding']
            confidence = result['confidence']
            # 尝试多种编码方式
            if detected_encoding and confidence > 0.7:
                try:
                    text = content.decode(detected_encoding)
                    print(f"文件 {file_path} 使用检测到的编码 {detected_encoding} 解码成功")
                except UnicodeDecodeError:
                    text = content.decode('utf-8', errors='ignore')
                    print(f"文件 {file_path} 使用 {detected_encoding} 解码失败，强制使用 UTF-8 忽略非法字符")

            else:
                # 尝试多种常见编码
                encodings = ['utf-8', 'gbk', 'gb18030', 'gb2312', 'latin-1', 'utf-16', 'cp936', 'big5']
                text = None
                for encoding in encodings:
                    try:
                        text = content.decode(encoding)
                        print(f"文件 {file_path} 使用 {encoding} 解码成功")
                        break
                    except UnicodeDecodeError:
                        continue
                        # 如果所有编码都失败，使用忽略错误的方式解码
                if text is None:
                    text = content.decode('utf-8', errors='ignore')
                    print(f"警告：文件 {file_path} 使用 UTF-8 忽略非法字符")
        text = clean_text(text)
        return text
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        traceback.print_exc()
        return f"处理文件 {file_path} 失败：{str(e)}"


import os


def get_all_files(folder_path):
    files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            files.append(file_path)
    return files

def read_json(file_path):
    jaon_read=json.load(open(file_path,encoding='utf-8'))
    print(jaon_read)
    reslut=[]
    for i in jaon_read:
        reslut.append(i)
    return reslut
def write_json(datasets,file):
    with open(file, 'w', encoding='utf-8') as outfile:
        json.dump(datasets, outfile, ensure_ascii=False, indent=4)
def process_and_index_files(file_objs,kb_name):
    # 确保知识库目录存在
    kb_dir = os.path.join(KB_BASE_DIR, kb_name)
    os.makedirs(kb_dir, exist_ok=True)


    print('文件夹：----',kb_name)

    # 设置临时处理文件路径
    # semantic_chunk_output = os.path.join(OUTPUT_DIR, "semantic_chunk_output.json")
    semantic_chunk_vector = os.path.join(kb_dir, "semantic_chunk_vector.json")

    # 设置知识库索引文件路径
    semantic_chunk_index = os.path.join(kb_dir, "semantic_chunk.index")
    semantic_chunk_metadata = os.path.join(kb_dir, "semantic_chunk_metadata.json")

    all_chunks = []
    error_messages = []
    kb_dir = os.path.join(KB_BASE_DIR, kb_name)
    # file_datasets=get_all_files(kb_dir)
    # for file_objs in file_datasets:
    # if file_objs.endswith('.index') or  file_objs.endswith('.py'):continue
    # name=file_objs.split('\\')[-1]
    # if name== "semantic_chunk_metadata.json":
    #     read_json=json.load(open(name))
    # print(name)
    # if not file_objs or len(file_objs) == 0:
    #     return "错误：没有选择任何文件"
    print(file_objs)
    name=file_objs[0].split('\\')[-1]
    print(name)
    print(f"开始处理 {len(file_objs)} 个文件，目标知识库: {kb_name}...")

    '''分布式处理分块，每段词'''
    with ThreadPoolExecutor(max_workers=4) as executor:
        ###process_upload_to_kb解析上穿文件，编码也要输出成输入的格式
        future_to_file={executor.submit(process_upload_to_kb, file_obj.name):file_obj for file_obj in file_objs}
        for future in as_completed(future_to_file):
            result = future.result()

            file_obj = future_to_file[future]
            file_name =file_obj.name
            ##排除原因
            if isinstance(result, str) and result.startswith("处理文件"):
                error_messages.append(result)
                print(result)
                continue
            # 检查结果是否为有效文本
            if not result or not isinstance(result, str) or len(result.strip()) == 0:
                error_messages.append(f"文件 {file_name} 处理后内容为空")
                print(f"警告: 文件 {file_name} 处理后内容为空")
                continue
            '''进行分块处理'''
            print(f"对文件 {file_name} 进行语义分块...")
            chunks = semantic_chunk(result,800,20,name)
            if not chunks or len(chunks) == 0:
                error_messages.append(f"文件 {file_name} 无法生成任何分块")
                print(f"警告: 文件 {file_name} 无法生成任何分块")
                continue
            # 将处理后的文件保存到知识库目录
            file_basename = os.path.basename(file_name)
            dest_file_path = os.path.join(kb_dir, file_basename)

            try:
                shutil.copy2(file_name, dest_file_path)
                print(f"已将文件 {file_basename} 复制到知识库 {kb_name}")
            except Exception as e:
                print(f"复制文件到知识库失败: {str(e)}")
            all_chunks.extend(chunks)
            print(f"文件 {file_name} 处理完成，生成 {len(chunks)} 个分块")
    '''使用停用词，看块内的内容是否是有效，过长截断'''
    if not all_chunks:
        return "所有文件处理失败或内容为空\n" + "\n".join(error_messages)
    # 确保分块内容干净且长度合适，使用停用词，分词过长切断
    valid_chunks = []
    for chunk in all_chunks:
        # 深度清理文本
        clean_chunk_text = clean_text(chunk["chunk"])  ##去除一些不用的字词

        # 检查清理后的文本是否有效
        if clean_chunk_text and 1 <= len(clean_chunk_text) <= 8000:
            chunk["chunk"] = clean_chunk_text
            valid_chunks.append(chunk)
        elif len(clean_chunk_text) > 8000:
            # 如果文本太长，截断它
            chunk["chunk"] = clean_chunk_text[:8000]
            valid_chunks.append(chunk)
            print(f"警告: 分块 {chunk['id']} 过长已被截断")
        else:
            print(f"警告: 跳过无效分块 {chunk['id']}")

    if not valid_chunks:
        return "所有生成的分块内容无效或为空\n" + "\n".join(error_messages)
    print(f"处理了 {len(all_chunks)} 个分块，有效分块数: {len(valid_chunks)}")
    print(valid_chunks)



    '''报错语义块json和词向量的json'''
    try:
        read_datasets=read_json(semantic_chunk_metadata)
        write_json(read_datasets+valid_chunks,semantic_chunk_metadata)
    except:
        with open(semantic_chunk_metadata, 'w', encoding='utf-8') as json_file:
            json.dump(valid_chunks, json_file, ensure_ascii=False, indent=4)
    print(f"语义分块完成: {semantic_chunk_metadata}")
    # 向量化语义分块
    print(f"开始向量化 {len(valid_chunks)} 个分块...")
    vectorize_file(valid_chunks, semantic_chunk_vector,name=name)##分段的块，保存路径
    print(f"语义分块向量化完成: {semantic_chunk_vector}")



    # 验证向量文件是否有效
    try:
        with open(semantic_chunk_vector, 'r', encoding='utf-8') as f:
            vector_data = json.load(f)

        if not vector_data or len(vector_data) == 0:
            return f"向量化失败: 生成的向量文件为空\n" + "\n".join(error_messages)

        # 检查向量数据结构
        if 'vector' not in vector_data[0]:
            return f"向量化失败: 数据中缺少向量字段\n" + "\n".join(error_messages)

        print(f"成功生成 {len(vector_data)} 个向量")
    except Exception as e:
        return f"读取向量文件失败: {str(e)}\n" + "\n".join(error_messages)



    #构建索引
    print(f"开始为知识库 {kb_name} 构建索引...")
    build_faiss_index(semantic_chunk_vector, semantic_chunk_index, semantic_chunk_metadata,name=name)
    print(f"知识库 {kb_name} 索引构建完成: {semantic_chunk_index}")
    status = f"知识库 {kb_name} 更新成功！共处理 {len(valid_chunks)} 个有效分块。\n"
    return status



    # except Exception as e:
    #     error = f"知识库 {kb_name} 索引构建过程中出错：{str(e)}"
    #     print(error)
    #     traceback.print_exc()
    #     return error + "\n" + "\n".join(error_messages)

def update_status(is_processing=True, is_error=False):
    if is_processing:
        return '<div class="status-box status-processing">正在处理您的问题...</div>'
    elif is_error:
        return '<div class="status-box status-error">处理过程中出现错误</div>'
    else:
        return '<div class="status-box status-success">回答已生成完毕</div>'






'''对话处理'''
