from  config import consult_config
import sys
import os
import asyncio
import time
import httpx
import requests
import json
import random
import copy
from NewDB import *
from datetime import datetime
import openai
from openai import AsyncOpenAI,OpenAI
#导入工具类
from tools_definition import tool_config
from function_utils import stream_string, get_next_message_by_slots, \
    FunctionCallSummaryConfig, sort_nested_dict, deepseek_chat_completion, deepseek_chat_completion_norm_chat

from config import consult_config
tool_config=tool_config()
tool_list=tool_config.tools_list
config=consult_config()

print(tool_list)
check_functions =  {"get_academic_info":FunctionCallSummaryConfig.get_academic_info,
                    "get_major_info":FunctionCallSummaryConfig.get_major_info,
                    "get_object_info":FunctionCallSummaryConfig.get_object_info,
                    "get_scholarship_info":FunctionCallSummaryConfig.get_scholarship_info,
                    "get_budget_info":FunctionCallSummaryConfig.get_budget_info,
                    "get_other_info":FunctionCallSummaryConfig.get_other_info}
system_prompt = "你是一个从聪明的人工智能助手，你能将用户的输入进行拆解，并调用插件获取信息"
groupid_slots_dict={}
async def chat_round(current_message,history,groupId="12"): #question, history   current_message,history
    print("current_message:", current_message)
    current_time = str(datetime.now())
    db_client = await connect()  # 连接数据库
    '''删除sql的12用户'''
    conn = await connect()
    try:
        await DEL_SlotInfo(conn, "slot_info_table", groupId)
        await close_db(db_client)  # 关闭数据库连接
    except:
        pass


    past_filled_slots = await Read_SlotInfo(db_client, table_name=config.slot_table_name, group_id=groupId)
    if past_filled_slots:
        past_filled_slots = past_filled_slots[0]
        all_filled_slots = copy.deepcopy(json.loads(past_filled_slots['slot_info_dict']))  # 获取 slots_info_dict 字段的值
        all_filled_slots = sort_nested_dict(input_dict=all_filled_slots)
        print("历史该用户槽位填充结果：", past_filled_slots)
    else:
        all_filled_slots = copy.deepcopy(tool_config.slot_dict)
        print("json.dumps(tool_config.slot_dict):", tool_config.slot_dict)
        insert_params=(groupId, json.dumps(tool_config.slot_dict),current_time,"中介留学")
        await insert_SlotInfo(db_client, table_name=config.slot_table_name, data_to_insert=insert_params)
    # 排个序
    all_filled_slots = sort_nested_dict(input_dict=all_filled_slots)
    print(f"本轮初始情况下的用户槽位:,{all_filled_slots}")

    # 对于首轮消息,发送固定引导语





    if len(history) == 0:
        await close_db(db_client)
        # 您是否有心仪的留学院校？您计划申请本科、硕士、博士学位呢？
        introduce_message = "欢迎来到老刘留学中介，我是您的个人助理小刘，能快速为您办理中介留学，请问您是否有心仪的留学院校？您计划申请本科、硕士、博士学位呢？"
        print("introduce_message:", introduce_message)
        async for chunk in stream_string(introduce_message, chunk_size=3):
            yield chunk
        # history.append({"role": "assistant", "content": introduce_message})
        return#拼接系统提示词
    new_history_list = []
    new_history_list.append({"role": "system", "content": system_prompt})
    new_history_list.extend(history) #追加上历史记录
    new_history_list.append({"role":"user","content":current_message})
    # 存放本轮对话触发的所有工具调用的函数中缺失的参数
    total_missing_field=[]
    accumulate_message=""
    tool_calls_dict = {} #存放单一工具调用的信息
    complete_tool_calls=[] #存放所有工具调用的信息
    is_first_call=False

    async for chunk in deepseek_chat_completion(tool_list, new_history_list):
        # print("origin_chunk:",chunk)
        if chunk.choices:  # 元数据不要
            if chunk.choices[0].delta.tool_calls:##使用到工具
                for tool_call in chunk.choices[0].delta.tool_calls:
                    tool_call_id = tool_call.id
                    function_name = tool_call.function.name
                    arguments_fragment = tool_call.function.arguments
                    # print("arguments_fragment:", arguments_fragment)
                    # 初始化工具调用信息 tool_call_id为None的话也不开一个新的key
                    if tool_call_id not in tool_calls_dict and tool_call_id:
                        tool_calls_dict[tool_call_id] = {
                            "name": function_name,
                            "arguments": ""
                        }
                    # print("触发functioncalling回复:", chunk.choices[0].delta.tool_calls)
                    if tool_call_id and arguments_fragment:
                        tool_calls_dict[tool_call_id]["arguments"] += arguments_fragment
                    #此时arguments_fragment为None
                    elif not arguments_fragment:
                        continue
                    else:
                        # 获取最后一个有key的值,
                        last_key_id = list(tool_calls_dict.keys())[-1]
                        tool_calls_dict[last_key_id]["arguments"] += arguments_fragment

            if chunk.choices[0].delta.content:  # 检查是否有内容决定是function call还是不同回复,没用到工具
                accumulate_message += chunk.choices[0].delta.content
                # print("触发普通问答回复:", chunk.choices[0].delta.content)
                if chunk.choices[0].finish_reason == "stop":
                    yield chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content  # + "\n"

            if chunk.choices[0].finish_reason == "tool_calls":###所有的工具集合
                print("工具调用结束")
                for tool_call_id, tool_call_info in tool_calls_dict.items():
                    arguments = json.loads(tool_call_info["arguments"])
                    if arguments:
                        complete_tool_calls.append({
                            "id": tool_call_id,
                            "name": tool_call_info["name"],
                            "arguments": arguments
                        })
                    print("************",complete_tool_calls)
    print(f"本轮调用的所有工具列表:{complete_tool_calls}")

    function_name_list = []
    is_slot_changed_for_half_generation = False
    if complete_tool_calls:
        print('发生了工具调用')
        whole_function_response = ""
        # 槽位缺失时反问的话术
        format_message1 = random.choice(["十分感谢提供：\n", "好的，我已记录：\n", "感谢提供：\n", "收到反馈：\n"])
        current_round_slots_info = format_message1

        for tool_call in complete_tool_calls:
            one_tool_missing_fields = []
            function_name = tool_call.get("name", "")
            function_name_list.append(function_name)
            function_args = tool_call.get("arguments", "")
            one_tool_missing_fields.extend([k.strip() for k in tool_config.slot_dict.get(function_name, [])])
            # print('function_args--function_args',function_args)
            for key, value in function_args.items():
                original_value = all_filled_slots[function_name].get(key, "")###历史数据
                print(original_value,str(value))
                if  str(original_value) != str(value):###历史数据和当前数据不一样，更新当前数据

                    is_slot_changed_for_half_generation = True  # 槽位信息发生改变标识符号
                    all_filled_slots[function_name].update({key: value})  # 历史槽位信息的调整与补充
                    # print('进入',all_filled_slots)
                    temp_str = str(tool_config.params_schema.get(key))
                    current_round_slots_info += f"{temp_str}:{value}\n"
                # if value != "" and str(value) not in ["未提到", "未提供",""," "]:
                #     one_tool_missing_fields.remove(key)
                #     function_args[key] = original_value
                #     continue


                if key in one_tool_missing_fields:one_tool_missing_fields.remove(key)

            function_to_call = check_functions[function_name]
            print('999999999999999999',function_name)
            if len(one_tool_missing_fields) != len(
                    [k.strip() for k in tool_config.slot_dict.get(function_name, [])]) and len(
                    one_tool_missing_fields) > 0:
                print("当前函数缺失部分槽位，需要继续搜集参数")
                total_missing_field.extend(one_tool_missing_fields)
                function_response = 'no_slots_info'
            elif len(one_tool_missing_fields) == 0:
                function_response = function_to_call(**function_args)
                # print("函数调用执行结果function response:", function_response)
                if '未提到' in function_response:function_response = function_response.replace("未提到", "")
            else:print("当前函数缺失全量槽位,说明模型未提到任何参数，需要继续反问列表");function_response="no_slots_info"

            if function_response not in "".join([str(k.get("content", "")) for k in new_history_list
                                                 if k.get("role", "") == "assistant"]):
                whole_function_response += function_response
            else:
                print("历史调用过相同的function call的结果,没必要重复总结和进行工具调用")

        '''# 将更新完的槽位update到数据库'''
        db_client=await connect()  # 连接数据库
        print(all_filled_slots)
        await update_SlotInfo(db_client, table_name=config.slot_table_name, group_id=groupId,
                              slot_info_dict=json.dumps(all_filled_slots), created_time=current_time)
        await close_db(db_client)  # 关闭数据库连接


        print('缺失的：--',total_missing_field)

        # 将缺失的所有槽位追加形成本轮模板化反问，顺着用户的话题向下走 (1) 绩点 \n (2) 专业
        if total_missing_field:###一个完整的草甸单独缺少的时候，额外通过中英文的object字典查找
            ask_message = '\n'.join(
                [f"{i + 1}. {tool_config.params_schema.get(key)}" for i, key in enumerate(total_missing_field)])
            format_message = random.choice(
                ["\n收到，请进一步提供", '\n明白，麻烦您告知一下', '\n还得辛苦您补充一下', '\n能否麻烦您再提供',
                 '\n方便的话，还希望您能提供'])
            missing_slot_ask_prompt = current_round_slots_info + f"{format_message}:\n{ask_message}\n"
            async for chunk in stream_string(missing_slot_ask_prompt, chunk_size=3):
                yield chunk  # +"\n"
            return
        else:  # 如果没有缺失的槽位则完成本次业务,进行总结
            next_collect_slot_list, is_all_field_missing_flag, theme = get_next_message_by_slots(all_filled_slots)
            if next_collect_slot_list:  # 如果有接下来需要搜集信息的槽位
                # if is_first_call:
                #     next_message=""   #introduction
                # else:
                # 如果有调用function得到返回结果需要进行总结:
                if whole_function_response:
                    prefix_summary = random.choice(['已收到您的反馈：\n', "感谢告知：\n", "感谢提供信息：\n"])
                else:
                    prefix_summary = ""
                # 如果有部分槽位缺失走拼接话术
                if not is_all_field_missing_flag:  # False
                    format_message = random.choice(["方便说下", '我们继续，', '另外，', '', '那么，', '我还想知道'])
                    inadequte_message = "、".join(
                        [f"{tool_config.params_schema.get(key)}" for i, key in enumerate(next_collect_slot_list)])
                    # 如果试用期开始时间与试用期结束时间同时在文本串中则需要改成试用期起止时间
                    print("下一个需要问的主题为:", theme, "标准话术:", inadequte_message)
                else:  # 如果全部槽位缺失走预定义话术逻辑 #这里需要实例化随机询问下一步补充信息的话术
                    inadequte_message = tool_config.main_question_schema.get(theme, "")
                    print("下一个需要问的主题为:", theme, "标准话术:", inadequte_message)
                    format_message = ""
                next_message = prefix_summary + whole_function_response + f"\n{format_message}".strip() + inadequte_message.strip()
                print("next_message:", next_message)
                # print(f"总结收到的信息,并拉起下一步需要搜集的信息:{next_message}")
                async for chunk in stream_string(next_message, chunk_size=3):
                    yield chunk  # + "\n"
                # history.append({"role": "assistant", "content": next_message})
                return
            # 如果没有解析的槽位说明信息都已经搜集完整了如果本轮槽位信息发生了改变
            elif not next_collect_slot_list and is_slot_changed_for_half_generation:
                all_filled_slots = sort_nested_dict(input_dict=all_filled_slots)
                new_all_filled_slots = all_filled_slots.copy()
                print("信息已经搜集完成且槽位信息发生更新,则重新总结内容:",new_all_filled_slots)

                '''构造'''

                mess = ''


                print(all_filled_slots)

                for k, v in all_filled_slots.items():
                    for key, val in v.items():
                        if key=='intention_school':key='申请的学校是'
                        if key == 'academic_degree': key = '申请的学历是'
                        if key == 'current_school': key = '目前所在学校是'
                        if key == 'gpa_point': key = 'gpa是'
                        mess += f"{key}:{val}"+';'

                ''''''
                mess +='在这个基础上还需要问一些什么 '
                # finished_yw_message = tool_config.final_message_template["conclusion_message"].format(
                #     *[value for category in new_all_filled_slots.values() for value in category.values()]
                # )
                print(f"发送告知用户信息搜集完成,等待人工客服人员后续联系的话术:{mess}")
                async for chunk in stream_string(mess, chunk_size=3):
                    yield chunk  # + "\n"
                # history.append({"role": "assistant", "content": finished_yw_message})
                # 调用API
                return
            # 如果没有槽位缺失并且历史槽位没有发生改变则调用没有工具的LLM自由对话.
            else:
                # print("-------仅对本轮会话进行问答----",accumulate_message)
                conn = await connect()
                result=await Read_SlotInfo(conn,"slot_info_table",groupId)
                await close_db(db_client)  # 关闭数据库连接
                mess=''
                # if len(new_history_list)>=1:
                #     for infomation in  new_history_list:
                #         for key,values in infomation.items():mess+=values+';'
                #     mess=';'.join(mess.split(';')[-2:])+'已知道的信息'
                #     a = json.loads(result[0]['slot_info_dict'])
                #     for k, v in a.items():
                #         for key, val in v.items():
                #             mess+=f"{key}:{val}"
                for k, v in all_filled_slots.items():
                    for key, val in v.items():
                        if key=='intention_school':key='申请的学校是'
                        if key == 'academic_degree': key = '申请的学历是'
                        if key == 'current_school': key = '目前所在学校是'
                        if key == 'gpa_point': key = 'gpa是'
                        mess += f"{key}:{val}"+';'

                messages_ = [
                    {"role": "system", "content": "我是留学助手，根据以下内容推荐合适的学校以及入学时间和金额"},
                    # {"role": "user", "content": "你好"},
                    {"role": "user", "content": mess},
                ]
                print(mess)
                print(messages_)
                async for chunk in deepseek_chat_completion_norm_chat(messages=messages_):
                    # print("槽位已经搜集完成且本轮会话槽位信息没有发生改变,仅对本轮会话进行问答",chunk.choices[0].delta.content)
                    # print(new_history_list[-2:])
                    # print(chunk)
                    accumulate_message += chunk
                    yield chunk  # + "\n"
                # history.append({"role": "assistant", "content": accumulate_message})

                return









