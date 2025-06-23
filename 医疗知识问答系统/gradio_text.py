import re

import gradio as gr
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core.node_parser import SentenceSplitter


def greet(name):
    return "Hello " + name + "!"
# iface=gr.Interface(fn=greet, inputs=gr.Textbox(), outputs=gr.Textbox())
# iface.launch()
'''https://zhuanlan.zhihu.com/p/679668818'''

import concurrent.futures
import time


# 定义一个函数，该函数将被多个线程执行
def task(n):
    time.sleep(1)  # 模拟耗时操作
    return f"Task {n} completed"


# # 创建ThreadPoolExecutor实例，指定最大线程数
# with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#     # 提交多个任务到线程池
#     # futures = {executor.submit(task, i):i for i in range(10)}
#     futures = [executor.submit(task, i) for i in range(10)]
#     print(futures)
#     # 等待所有任务完成，并收集结果
#     for future in concurrent.futures.as_completed(futures):
#         print(future.result())

import re
from llama_index.core.node_parser import SentenceSplitter
import typing

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

# 测试文本
test_text = """
这是一个测试句子！这是第二个句子？这是第三个句子；这可能是最后一个句子。
当然，这也可以是一个新段落。
"""

# 使用 EnhancedSentenceSplitter 分割文本
result = text_splitter.split_text(test_text)

# 打印结果
print("分割后的文本块：")
for i, chunk in enumerate(result):
    print(f"Chunk {i+1}: {chunk}")
