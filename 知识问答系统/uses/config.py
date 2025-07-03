import os


class Config():
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    ###retrievor参数
    topd=3
    topt=6
    maxlen = 128  # 召回文本片段的长度
    topk = 5  # query召回的关键词数量
    bert_path = '/workspace/model/embedding/tao-8k'
    recall_way = 'embed'  # 召回方式 ,keyword,embed

    # generator参数
    max_source_length = 767  # 输入的最大长度
    max_target_length = 256  # 生成的最大长度
    model_max_length = 1024  # 序列最大长度

    # embedding API 参数 - 用于 text2vec.py
    use_api = True  # 是否使用API而非本地模型
    api_key = "sk-07b0bbfd24bf4cb391cad5da8da05f6f"
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model_name = "text-embedding-v3"
    dimensions = 1024
    batch_size = 10

    # LLM API 参数 - 用于 rag.py
    llm_api_key = "sk-07b0bbfd24bf4cb391cad5da8da05f6f"  # 与embedding共用同一个key
    llm_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 与embedding共用同一个URL
    llm_model = "qwen-plus"  # 默认使用的LLM模型

    # 知识库配置
    kb_base_dir = "knowledge_bases"  # 知识库根目录
    default_kb = "default"  # 默认知识库名称

    # 输出目录配置 - 现在用作临时文件目录
    output_dir = "output_files"