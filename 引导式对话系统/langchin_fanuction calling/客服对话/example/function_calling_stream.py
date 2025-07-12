from openai import OpenAI,AsyncOpenAI
client = OpenAI(base_url="https://api.302.ai/v1/chat/completions", api_key="sk-gPl43py4bj6TN3mksIN18FPbRZXdHoV6i0XOAAshKFpanIb1")#ollama服务默认端口
response = client.chat.completions.create(model='gpt-4.1',
                                          messages=[
                                              {"role": "system", "content": "You are a helpful assistant"},
                                              {"role": "user", "content": "Hello"},
                                          ],
                                          stream=False  # 先将stream(流式输出)设置为False
                                          )
def get_weahter(location):
   if location=="Shanghai":
       return "sunny"
   elif location=="Beijing":
       return "rainy"
   else:
       return f"I don't know the weahter of location {location}"
def get_visiting_place(visiting_place):
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

#可以调用的工具字典,通过名称name找到对应的工具函数实现
check_functions =  {"get_weather":get_weahter,
                    "get_visiting_place":get_visiting_place}
response1 = client.chat.completions.create(
    model='gpt-4.1',
    messages=[
          {"role": "system", "content": "You are a helpful assistant"},
        # {"role": "user", "content": "你好"},
           {"role": "user", "content": "我想去北京玩,请问北京的天气如何？我想去故宫玩"},
      ],
    stream=False , # 先将stream(流式输出)设置为False,
    tools=tools,
     )
if response1.choices[0].finish_reason == "tool_calls":
    for i in response1.choices[0].message.tool_calls:
        tool_name = i.function.name
        tool_args = i.function.arguments
        tool_args = eval(tool_args)
        tool_result = check_functions[tool_name](**tool_args)
        print("调用的工具:", tool_name, "槽位参数:", tool_args, "工具调用结果:", tool_result)
else:  # 没有触发工具调用
    return_message = response1.choices[0].message.content
    print("未触发工具调用，直接回复:", return_message)
