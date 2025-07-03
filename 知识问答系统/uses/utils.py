import os.path
import re
import shutil

from 大模型.RAG.Advanced_product.医疗知识问答系统.uses.config import Config
from .chat import process_question_with_reasoning
KB_BASE_DIR=Config.kb_base_dir
os.makedirs(KB_BASE_DIR, exist_ok=True)

DEFAULT_KB = Config.default_kb
DEFAULT_KB_DIR = os.path.join(KB_BASE_DIR, DEFAULT_KB)
os.makedirs(DEFAULT_KB_DIR, exist_ok=True)
def get_knowledge_bases(KB_BASE_DIR,DEFAULT_KB):
    try:
        if not os.path.exists(KB_BASE_DIR):os.makedirs(KB_BASE_DIR,exist_ok=True)
        kb_dirs=[d for d in os.listdir(KB_BASE_DIR) if os.path.isdir(os.path.join(KB_BASE_DIR,d))]

        if DEFAULT_KB not in kb_dirs:
            os.makedirs(os.path.join(KB_BASE_DIR, DEFAULT_KB), exist_ok=True)

        return sorted(kb_dirs)
    except Exception as e:
        print(f"获取知识库列表失败: {str(e)}")
        return [DEFAULT_KB]
def create_knowledge_base(kb_name: str,KB_BASE_DIR):
    try:
        if not kb_name or not kb_name.strip():
            return "错误：知识库名称不能为空"

        # 净化知识库名称，只允许字母、数字、下划线和中文
        kb_name = re.sub(r'[^\w\u4e00-\u9fff]', '_', kb_name.strip())

        kb_path = os.path.join(KB_BASE_DIR, kb_name)
        print(kb_path)
        if os.path.exists(kb_path):
            return f"知识库 '{kb_name}' 已存在"

        os.makedirs(kb_path, exist_ok=True)
        return f"知识库 '{kb_name}' 创建成功"
    except Exception as e:
        return f"创建知识库失败: {str(e)}"


def delete_knowledge_base(kb_name,DEFAULT_KB,KB_BASE_DIR):
    try:
        if kb_name==DEFAULT_KB:
            return f"无法删除默认知识库 '{DEFAULT_KB}'"
        kb_path=os.path.join(KB_BASE_DIR,kb_name)
        if not os.path.exists(kb_path):
            return f"知识库 '{kb_name}' 不存在"
        shutil.rmtree(kb_path)
        return f"知识库 '{kb_name}' 已删除"
    except Exception as e:
        return f"删除知识库失败: {str(e)}"

# 获取知识库文件列表
def get_kb_files(kb_name) :
    """获取指定知识库中的文件列表"""
    try:
        kb_path = os.path.join("knowledge_bases", kb_name)
        if not os.path.exists(kb_path):
            return []

        # 获取所有文件（排除索引文件和元数据文件）
        files = [f for f in os.listdir(kb_path)
                 if os.path.isfile(os.path.join(kb_path, f)) and
                 not f.endswith(('.index', '.json'))]

        return sorted(files)
    except Exception as e:
        print(f"获取知识库文件列表失败: {str(e)}")
        return []

# 更新知识库文件列表
def update_kb_files_list(kb_name):
    if not kb_name:
        return "未选择知识库"
    files = get_kb_files(kb_name)
    kb_dir = os.path.join(KB_BASE_DIR, kb_name)
    has_index = os.path.exists(os.path.join(kb_dir, "semantic_chunk.index"))

    if not files:
        files_str = "知识库中暂无文件"
    else:
        files_str = "\n".join([f"{i+1}. {file}" for i, file in enumerate(files)])
    index_status = "\n\n**索引状态:** " + ("✅ 已建立索引" if has_index else "❌ 未建立索引")
    return f"### 知识库: {kb_name}\n\n{files_str}{index_status}"

# 知识库选择变化时
def on_kb_change(kb_name):
    if not kb_name:
        return "未选择知识库", "选择知识库查看文件..."

    kb_dir = os.path.join(KB_BASE_DIR, kb_name)
    has_index = os.path.exists(os.path.join(kb_dir, "semantic_chunk.index"))
    status = f"已选择知识库: {kb_name}" + (" (已建立索引)" if has_index else " (未建立索引)")

    # 更新文件列表
    files_list = update_kb_files_list(kb_name)

    return status, files_list

from .knowlage_datasets import process_and_index_files, update_status


def batch_upload_to_kb(file_objs, kb_name) :
    """批量上传文件到指定知识库并进行处理"""
    try:
        if not kb_name or not kb_name.strip():
            return "错误：未指定知识库"

        # 确保知识库目录存在
        kb_dir = os.path.join(KB_BASE_DIR, kb_name)
        if not os.path.exists(kb_dir):
            os.makedirs(kb_dir, exist_ok=True)

        if not file_objs or len(file_objs) == 0:
            return "错误：未选择任何文件"

        return process_and_index_files(file_objs, kb_name)
    except Exception as e:
        return f"上传文件到知识库失败: {str(e)}"
def process_upload_to_kb(files, kb_name):
    if not kb_name:
        return "错误：未选择知识库"
    result = batch_upload_to_kb(files, kb_name)
    files_list = update_kb_files_list(kb_name)
    return result, files_list


'''对话'''
def process_and_update_chat(question, kb_name, use_search, use_table_format, multi_hop, chat_history):
    ####输入，选择知识库，启用联网搜索，启用表格格式化，启用多跳，聊天历史
    if not question.strip():
        return chat_history, update_status(False, True), "等待提交问题..."
    chat_history.append([question, "正在思考..."])
    yield chat_history, update_status(True), f"开始处理您的问题，使用知识库: {kb_name}..."

    # 用于累积检索状态和答案
    last_search_display = ""
    last_answer=""
    print(chat_history)
    # 处理问题并更新对话历史
    for search_display, answer in process_question_with_reasoning(question, kb_name, use_search, use_table_format, multi_hop, chat_history[:-1]):
        # 更新检索状态和答案
        last_search_display = search_display

        if chat_history:
            chat_history[-1][1] = answer
            yield chat_history, update_status(True), search_display

    # 处理完成，更新状态
    yield chat_history, update_status(False), last_search_display
