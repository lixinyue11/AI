class consult_config():
    #调用的LLM API-KEY
    api_key="sk-gPl43py4bj6TN3mksIN18FPbRZXdHoV6i0XOAAshKFpanIb1" #大模型的API_KEY
    base_url="https://api.302.ai/v1/chat/completions"#大模型的反向代理地址
    db_host ="localhost"    # 改成自己的数据库地址eg:"122.43.174.198"
    dbname = "Dialogue_system"  #改成自己的槽位表所在的数据库名称
    db_port=5432 #数据库端口号
    user ="postgres"  #数据库用户名
    password = "jiuzheyang88" #改成自己设置的数据库密码
    #槽位表
    slot_table_name="slot_info_table"