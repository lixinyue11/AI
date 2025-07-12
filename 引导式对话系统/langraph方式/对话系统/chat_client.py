import asyncio
from chat import main

async def stream_string(s, chunk_size=3):
    """
        异步流式输出字符串
        :param s: 输入的字符串
        :param chunk_size: 每次返回的块大小
        :return: 异步生成器，逐步返回字符串块"""
    for i in range(0, len(s), chunk_size):
        yield s[i:i + chunk_size]
        await asyncio.sleep(0.1)  # 每个chunk之间间隔0.1秒
async def chat_round(current_message, history):
    #TavilySearch=TavilySearchResults(max_results=1)

    if len(history) == 0:

        # 您是否有心仪的留学院校？您计划申请本科、硕士、博士学位呢？
        introduce_message = "欢迎来到老刘留学中介，我是您的个人助理小刘，能快速为您办理中介留学，请问您是否有心仪的留学院校？您计划申请本科、硕士、博士学位呢？"
        print("introduce_message:", introduce_message)
        async for chunk in stream_string(introduce_message, chunk_size=3):
            yield chunk
        # history.append({"role": "assistant", "content": introduce_message})
        return#拼接系统提示词
    system_prompt = "你是一个从聪明的人工智能助手，你能将用户的输入进行拆解，并调用插件获取信息"
    new_history_list = []
    custorm=[]
    new_history_list.append({"role": "system", "content": system_prompt})
    new_history_list.extend(history)  # 追加上历史记录
    new_history_list.append({"role": "user", "content": current_message})
    s=''
    for i in  new_history_list:
        for key,valu in i.items():s+=valu+';'
    a=main(s)
    # custorm.append(a)
    # result=';'.join(custorm)
    # print(result)
    yield  (a)




    # yield "正在生成结果..."




