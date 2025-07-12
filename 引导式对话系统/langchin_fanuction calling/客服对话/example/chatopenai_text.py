from typing import TypedDict, Annotated

from langchain_core.messages import ToolMessage, AnyMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, Runnable, RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import END, StateGraph, START
# api_key = "sk-07b0bbfd24bf4cb391cad5da8da05f6f"
# base_urlbase_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
# model="abab6.5t-chat",
# response=ChatOpenAI(
#
#     api_key=api_key,
#     base_url=base_urlbase_url,
#     stream=False
# )
# messages= {"role": "system", "content": "You are a helpful assistant"},
# llm=response.invoke(messages)
# print(response)
key= "sk-gPl43py4bj6TN3mksIN18FPbRZXdHoV6i0XOAAshKFpanIb1"
base_urlbase_url="https://api.302.ai/v1/chat/completions"
url='https://api.302.ai/v1/responses'
mode_gpt='gpt-4.1'
m='codex-mini-latest'
llm= ChatOpenAI(
    model=mode_gpt,
    api_key=key,
    base_url=base_urlbase_url,
    stream=False, #非流式输出
)
def get_weahter(location:str):
   if location=="Shanghai":
       return "sunny"
   elif location=="Beijing":
       return "rainy"
   else:
       return f"I don't know the weahter of location {location}"

def get_visiting_place(visiting_place:str):
    return f'I have order the ticket and we will go {visiting_place} on Thursday.'
tools=[{
        "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取当前位置的天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "中国的省份名称的拼音表示,第一个字大写如:Sichuan",
                            "default":"未提及"
                        },
                    }
                },
                "required": ["location"] #必填参数
            }
    },
    {
        "type": "function",
            "function": {
            "name": "get_visiting_place",
            "description": "获取去访问的景点",
            "parameters": {
                "type": "object",
                "properties": {
                    "visiting_place": {
                        "type": "string",
                        "description": "景点名称",
                    },
                }
            },
            "required": ["visiting_place"]  # 必填参数
        },
    }]

# 获取模型生成的回复
llm1= ChatOpenAI(
    model=mode_gpt,
    api_key=key,
    base_url=base_urlbase_url,
    stream=False, #非流式输出
    #tools=tools,
)
messages =  ChatPromptTemplate.from_messages([
{"role": "system", "content": "我是地理专家"},
{"role": "user", "content": "对{messages}进行天气经典的获取"},
])


check_functions =  {"get_weather":get_weahter,
                    "get_visiting_place":get_visiting_place}
tools=[get_weahter,get_visiting_place]
part_1_assistant_runnable=messages|llm1.bind_tools(tools)


events = part_1_assistant_runnable.invoke({"messages": "I love ShangHai"})
for i in part_1_assistant_runnable.stream( {"messages": ("user",  "I love ShangHai")}, stream_mode="values"):
    print(i)

