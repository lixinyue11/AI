"""
图形化界面部署服务,用于日常的开发、自测
pip install gradio

"""
import gradio as gr
import asyncio
from typing import AsyncGenerator, List, Tuple
from chat_process_client import chat_round
async def gradio_wrapper(message: str, chat_history : List[List[str]]) -> AsyncGenerator[str, None]:
    """
    Gradio适配器，将Gradio格式的历史记录转换为chat_round需要的格式
    message: 当前用户消息
    history: Gradio格式的历史记录 [[用户消息1, 机器人回复1], [用户消息2, 机器人回复2], ...]
    """
    # 转换历史记录格式
    print("chat_history:", chat_history)
    converted_history1 = [(h[0], h[1]) for h in chat_history] if chat_history else []
    converted_history = []
    if converted_history1:
        for elem in converted_history1:
            converted_history.append({"role":"user","content":elem[0]})
            converted_history.append({"role":"assistant","content":elem[1]})
    # 调用你的chat_round函数
    full_response = ""

    print('--------,messa------',message)
    async for chunk in chat_round(current_message=message, history=converted_history):
        full_response += chunk
        yield full_response  # 流式返回累积的完整响应


demo = gr.ChatInterface(
    fn=gradio_wrapper,
    examples=["你好", "我想咨询美国留学", "申请硕士需要什么条件？"], #FAQ问题,
    title="留学咨询助手",
    description="欢迎咨询留学相关问题，我将为您提供专业解答",
    chatbot=gr.Chatbot(
        bubble_full_width=False,
        avatar_images=(
            "https://example.com/user.png",  # 用户头像URL
            "https://example.com/bot.png"  # 机器人头像URL
        ),
        height=500,
        render_markdown=True
    ),
    textbox=gr.Textbox(
        placeholder="请输入您的问题...",
        container=False,
        scale=7,
        autofocus=True
    ),

)
# 启动应用
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", #任务其他服务可以访问该服务
        server_port=7777, #外网端口,端口
        share=True,#如果需要外网访问需要打开，网址:服务器公网ip地址(121.64.234.36..):端口号(7860)
    )