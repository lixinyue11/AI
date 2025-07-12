import sys
import os
import openai
from tools_definition import *
import asyncio
import time
import httpx
from  openai import AsyncOpenAI
from config import consult_config
import requests
config=consult_config()
async def stream_string(s, chunk_size=3):
    """
        异步流式输出字符串
        :param s: 输入的字符串
        :param chunk_size: 每次返回的块大小
        :return: 异步生成器，逐步返回字符串块"""
    for i in range(0, len(s), chunk_size):
        yield s[i:i + chunk_size]
        await asyncio.sleep(0.1)  # 每个chunk之间间隔0.1秒
# slot_dict = {"get_academic_info":{"intention_school":"美国哈佛","academic_degree":"研究生"},
#              "get_major_info": {"current_school": "哈尔滨工业大学","gpa_point":"3.8"},
#              "get_object_info": {"object_major": "","purpose":""},
#              "get_scholarship_info":{"is_scholarship":"是"},
#              "get_budget_info":{"academic_cost":"","living_cost":""},
#              "get_other_info":{"other_info":""}}
slot_dict={
"get_academic_info":{"intention_school":"美国哈佛","academic_degree":"研究生"},
"get_major_info": {"current_school": "哈尔滨工业大学","gpa_point":"3.8"},
}
def sort_nested_dict(input_dict,original_dict=slot_dict):
    """
    对嵌套字典进行排序，确保其键值对的顺序与原始字典一致。
    参数:
        original_dict (dict): 原始字典，用于定义排序顺序。
        input_dict (dict): 输入字典，需要被排序的字典。
    返回:
        dict: 排序后的字典。
    """
    sorted_dict = {}
    # 遍历原始字典的键
    for key in original_dict:
        if key in input_dict:
            # 如果键对应的值是字典，则递归排序
            if isinstance(input_dict[key], dict) and isinstance(original_dict[key], dict):
                sorted_dict[key] = sort_nested_dict(input_dict[key], original_dict[key])
            else:
                sorted_dict[key] = input_dict[key]
    print(sorted_dict)
    return sorted_dict
# slot_dict1 = {"get_major_info": {"current_school": "西北工业大学","gpa_point":"3.8"},
#             "get_academic_info":{"academic_degree":"研究生","intention_school":"普渡大学"},
#              "get_object_info": {"object_major": "","purpose":""},
#              "get_scholarship_info":{"is_scholarship":""},
#              "get_budget_info":{"academic_cost":"","living_cost":""},
#              "get_other_info":{"other_info":""}}
# sort_nested_dict(slot_dict1,slot_dict)
def get_next_message_by_slots(filled_slots):
    filled_slots = sort_nested_dict(input_dict=filled_slots)
    '''下一个空超微'''
    #下一句引导语的优先级是遍历所有槽位选择未填充完的槽位的进行遍历
    next_collect_slot_list=[]
    for theme,slot_value_dict in filled_slots.items():
        print(theme,slot_value_dict)
        for slot,value_elem in slot_value_dict.items():
            #如果有一个槽位为空,那么代表这个主题的槽位信息没有搜集完成则需要继续搜集;需要将该主题的所有为空的槽位搜集起来
            if value_elem=="":
                #获取对应的name
                next_collect_slot_list.append(slot)

        #如果这个主题槽位的信息有需要进行搜集的，则退出循环
        if next_collect_slot_list:
            # is_all_field_missing记录当前theme是否所有子主题槽位都缺失，这个标识将用于决定是否用该主题的话术进行询问
            if len(next_collect_slot_list)==len(slot_value_dict):
                is_all_field_missing = True
            else:
                is_all_field_missing = False
            return next_collect_slot_list,is_all_field_missing,theme
    #如果所有主题槽位信息都搜集完成后则返回空
    return [],False,''

slot_dict = {"get_academic_info":{"intention_school":"美国哈佛","academic_degree":"研究生"},
             "get_major_info": {"current_school": "","gpa_point":""},
             "get_object_info": {"object_major": "工业设计","purpose":""},
             "get_scholarship_info":{"is_scholarship":""},
             "get_budget_info":{"academic_cost":"","living_cost":""},
             "get_other_info":{"other_info":""}}

# print(get_next_message_by_slots(slot_dict))
class FunctionCallSummaryConfig:
    @staticmethod
    #总结目标院校信息
    def get_academic_info(intention_school,academic_degree):
        summary = f"""目标院校：{intention_school} 攻读学位:{academic_degree}
        """
        return summary
    @staticmethod
    def get_major_info(current_school,gpa_point):
        summary=f"""当前就读院校：{current_school} GPA绩点：{gpa_point}
        """
        return summary
    @staticmethod
    def get_object_info(object_major,purpose):
        summary=f"""目标专业：{object_major} 留学目的：{purpose}
        """
        return summary
    @staticmethod
    def get_scholarship_info(is_scholarship):
        summary=f"""是否申请奖学金：{is_scholarship}
        """
        return summary
    @staticmethod
    def get_budget_info(academic_cost,living_cost):
        summary=f"""学费预算：{academic_cost} 生活费预算：{living_cost}"""
        return summary
    @staticmethod
    def get_other_info(other_info):
        summary=f"""其他补充你信息：{other_info}
        """
        return summary
async def deepseek_chat_completion(tools, messages):
    # 官网deepseek
    deepseek_client = AsyncOpenAI(api_key=config.api_key, base_url="https://api.302.ai/v1/chat/completions")
    stream = await deepseek_client.chat.completions.create(
        model="gpt-4.1", #
        messages=messages,
        max_tokens=8000,
        temperature=0,
        stream=True,
        tools=tools,  # 工具列表
        tool_choice="auto",  # 工具调用方式
    )
    async for chunk in stream:
       # print("chunk:", chunk)
        yield chunk
async def deepseek_chat_completion_norm_chat(messages):
    # 官网deepseek
    # deepseek_client = AsyncOpenAI(api_key=config.api_key, base_url="https://api.302.ai/v1/chat/completions")
    # stream = await deepseek_client.chat.completions.create(
    #     model="gpt-4.1", #gpt-4.1
    #     messages=messages,
    #     max_tokens=8000,
    #     temperature=0,
    #     stream=True,

    # )
    from openai import OpenAI, AsyncOpenAI
    client = OpenAI(base_url="https://api.302.ai/v1/chat/completions",
                    api_key="sk-gPl43py4bj6TN3mksIN18FPbRZXdHoV6i0XOAAshKFpanIb1")  # ollama服务默认端口
    stream=client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    stream=False, #非流式输出
    )
    for chunk in stream:
        a = chunk
        if a[0] == 'choices':
            result = a[1][0].message.content
            yield result
