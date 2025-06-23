from openai import OpenAI
llm_api_key = "sk-07b0bbfd24bf4cb391cad5da8da05f6f"  # 与embedding共用同一个key
llm_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 与embedding共用同一个URL
llm_model = "qwen-plus"  # 默认使用的LLM模型
client_openai = OpenAI(
    api_key=llm_api_key,
    base_url=llm_base_url
)
chat_history=[]
for i in range(5):
    text=input('请输入：')
    if text=='ok':break
    chat_history.append([text, "正在思考..."])
    if chat_history and len(chat_history) > 0:
        context = "之前的对话内容：\n"
        for user_msg, assistant_msg in chat_history[-3:]:
            context += f"用户：{user_msg}\n"
            context += f"助手：{assistant_msg}\n"
        context += f"\n当前问题：{text}"
        enhanced_question = f"基于以下对话历史，回答用户的当前问题。\n{context}"
    else:
        enhanced_question = text
    print(enhanced_question)

    ###模型系统的prompt
    system_prompt = '''
            你是地理专家。基于提供用户的信息，我会回答相关的知识
            '''

    user_prompt = f'''
            {enhanced_question}背景信息：基于以上的背景信息和对话的历史回答用户的问题,只回答用户问题，不额外输出其他内容。
            '''

    response = client_openai.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    current_answer = response.choices[0].message.content.strip()
    print(current_answer)



