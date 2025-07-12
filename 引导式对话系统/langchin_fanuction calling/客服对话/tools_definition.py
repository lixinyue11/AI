
class tool_config():
    tools_list = [
        {"type": "function",
            "function": {
                "name": "get_academic_info",
                "description": "以第三人称提取用户目标院校与攻读学位",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intention_school": {
                            "type": "string",
                            "description": "提取目标院校,比如:美国哈佛,英国剑桥等",
                        },
                        "academic_degree": {
                            "type": "string",
                            "description": "提取攻读的学位",
                            "enum": ["高中","本科","研究生","博士生"]
                        },
                    }
                },
                "required": ["intention_school","academic_degree"]
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_major_info",
                "description": "以第三人称提取用户目前就读的国内院校、专业和GPA绩点",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "current_school": {
                            "type": "string",
                            "description": "提取用户当前就读的国内院校及专业，如：清华大学通信工程、复旦大学数学",
                        },
                        "gpa_point": {
                            "type": "string",
                            "description": "提取用户的GPA数值绩点,如:4.0,3.8等",
                        }
                    },
                    "required": ["current_school","gpa_point"]
                }
            }
        },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "get_object_info",
        #         "description": "以第三人称提取目标专业和留学目的",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "object_major": {
        #                     "type": "string",
        #                     "description": "提取国外目标专业,如：化学系",
        #                 },
        #                 "purpose": {
        #                     "type": "string",
        #                     "description": "提取留学目的,例如:深造、移民，提升就业竞争力",
        #                 },
        #             }
        #         },
        #             "required": ["object_major","purpose"]
        #     }
        # },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "get_scholarship_info",
        #         "description": "提取是否需要申请奖学金",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "is_scholarship": {
        #                     "type": "string",
        #                     "description": "提取是否申请奖学金",
        #                     "enum": ["是", "否"]
        #                 },
        #             }
        #         },
        #         "required": ["is_scholarship"]
        #     }
        # },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "get_budget_info",
        #         "description": "提取留学学费和生活费预算",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "academic_cost": {
        #                     "type": "string",
        #                     "description": "提取学费预算,格式:金额(货币)",
        #                 },
        #                 "living_cost": {
        #                     "type": "string",
        #                     "description": "提取生活费预算,格式:金额(货币)",
        #                 },
        #             }
        #         },
        #         "required": ["academic_cost","living_cost"]
        #     }
        # },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "get_other_info",
        #         "description": "提取用户补充说明的信息",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "other_info": {
        #                     "type": "string",
        #                     "description": "提取补充说明的信息。例如:没有了，希望住宿在外国人家里等",
        #                 },
        #             }
        #         },
        #         "required": ["other_info"]
        #     }
        # },

    ]

    """主题: 留学业务:
    1.留学目标与意向(get_academic_info)
    (1)您是否有心仪的留学院校？
    (2)您计划申请本科、硕士、博士学位呢？
    2.学业背景(get_major_info)
    (1) 您目前就读于国内哪个学校哪个专业？
    (2) 您当前的GPA是多少？
    3.专业与职业规划(get_object_info)
    (1) 您期望就读国外的什么专业
    (2) 留学的目的是什么(如：深造、移民，还是提升就业竞争力)
    4.经济与预算 (get_budget_info)
    预算范围:您每年的留学预算是多少？包括学费和生活费
    5.奖学金需求 (get_scholarship_info)
    是否需要申请奖学金或助学金？
    6.用户补充说明信息(get_other_info)
    """
    #主题模块问题话术:如果当前模块的所有槽位都没有搜集完成，则需要询问的问题
    main_question_schema={
        "get_academic_info":"您是否有心仪的留学院校？您计划申请本科、硕士、博士学位呢？",
        "get_major_info": "您目前就读于国内哪个学校哪个专业？当前的GPA是多少呢？",
        "get_object_info": "您期望就读国外的什么专业？留学目的是什么呢？",
        "get_budget_info":"您每年的留学预算是多少？包括学费和生活费",
        "get_scholarship_info":"是否需要申请奖学金或助学金？",
        "get_other_info":"还有什么需要补充说明的吗"
    }
    #所有信息搜集完后的引导语
    final_message_template = {"conclusion_message": """我们已清楚您的需求：
    留学院校：{}
    申请学位：{} 
    目前就读学习：{}
    当前GPA:{}
    期望就读专业:{}
    留学目的:{}
    预算范围:{}
    是否需要奖学金:{}
    正在定制化为您匹配学校中,请稍后......\n"""}
    #每个槽位的定义,用于后续当槽位缺失时反问时使用
    params_schema = {
        "intention_school":"目标院校",
        "academic_degree":"攻读学位",
        "current_school":"当前就读院校",
        "gpa_point":"GPA绩点",
        "object_major":"目标专业",
        "purpose":"留学目的",
        "is_scholarship":"是否申请奖学金",
        "academic_cost":"学费预算",
        "living_cost":"生活费预算",
        "other_info":"其他补充信息"
    }
    # 槽位列表，后续会话过程中本质上就是监控槽位的填充情况
    slot_dict = {"get_academic_info":{"intention_school":"","academic_degree":""},
                 "get_major_info": {"current_school": "","gpa_point":""},
                 "get_object_info": {"object_major": "","purpose":""},
                 "get_scholarship_info":{"is_scholarship":""},
                 "get_budget_info":{"academic_cost":"","living_cost":""},
                 "get_other_info":{"other_info":""}
                 }




