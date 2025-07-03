import os

import gradio as gr
from uses.css_ import js_code, custom_css
from uses.config import Config
from uses.utils import create_knowledge_base, delete_knowledge_base, update_kb_files_list, get_kb_files, on_kb_change, \
    process_upload_to_kb, process_and_update_chat

# 创建知识库根目录和临时文件目录
KB_BASE_DIR=Config.kb_base_dir
os.makedirs(KB_BASE_DIR, exist_ok=True)

DEFAULT_KB = Config.default_kb
DEFAULT_KB_DIR = os.path.join(KB_BASE_DIR, DEFAULT_KB)
os.makedirs(DEFAULT_KB_DIR, exist_ok=True)


def greet(name):
    return "Hello " + name + "!"
def get_knowledge_bases():
    try:
        if not os.path.exists(KB_BASE_DIR):os.makedirs(KB_BASE_DIR,exist_ok=True)
        kb_dirs=[d for d in os.listdir(KB_BASE_DIR) if os.path.isdir(os.path.join(KB_BASE_DIR,d))]

        if DEFAULT_KB not in kb_dirs:
            os.makedirs(os.path.join(KB_BASE_DIR, DEFAULT_KB), exist_ok=True)

        return sorted(kb_dirs)
    except Exception as e:
        print(f"获取知识库列表失败: {str(e)}")
        return [DEFAULT_KB]
def custom_theme():
    custom_theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="blue",
        neutral_hue="gray",
        text_size="lg",
        spacing_size="md",
        radius_size="md"
    )
    return custom_theme



with gr.Blocks(title="知识问答系统",theme=custom_theme(), elem_id="app-container", css=custom_css) as demo:#, css=custom_css
    with gr.Column(elem_id="header-container"):
        gr.Markdown("""
                # 🏥 医疗知识问答系统
                **智能医疗助手，支持多知识库管理、多轮对话、普通语义检索和高级多跳推理**  
                本系统支持创建多个知识库，上传TXT或PDF文件，通过语义向量检索或创新的多跳推理机制提供医疗信息查询服务。
                """)
        #添加javascript脚本文件
        gr.HTML(js_code, visible=False)
        # 使用State来存储对话历史
        chat_history_state = gr.State([])
        # 创建标签页
        with gr.Tabs() as tabs:
            # 知识库管理标签页
            with gr.TabItem("知识库管理"):
                with gr.Row():
                    # 左侧列：控制区
                    with gr.Column(scale=1, min_width=400):
                        gr.Markdown("### 📚 知识库管理与构建")

                        with gr.Row(elem_id="kb-controls"):
                            with gr.Column(scale=1):
                                new_kb_name = gr.Textbox(
                                    label="新知识库名称",
                                    placeholder="输入新知识库名称",
                                    lines=1
                                )
                                create_kb_btn = gr.Button("创建知识库", variant="primary", scale=1)
                            with gr.Column(scale=1):
                                current_kbs = get_knowledge_bases()
                                kb_dropdown = gr.Dropdown(
                                    label="选择知识库",
                                    choices=current_kbs,
                                    value=DEFAULT_KB if DEFAULT_KB in current_kbs else (current_kbs[0] if current_kbs else None),
                                    elem_classes="kb-selector"
                                )
                                with gr.Row():
                                    refresh_kb_btn = gr.Button("刷新列表", size="sm", scale=1)
                                    delete_kb_btn = gr.Button("删除知识库", size="sm", variant="stop", scale=1)

                            kb_status = gr.Textbox(label="知识库状态", interactive=False, placeholder="选择或创建知识库")
                        with gr.Group(elem_id="kb-file-upload", elem_classes="compact-upload"):
                            gr.Markdown('### 📄 上传文件到知识库 ')
                            file_upload=gr.File(
                                label="选择文件（支持多选TXT/PDF）",type='filepath',file_types=[".txt", ".pdf"],file_count="multiple",elem_classes="file-upload compact"
                            )
                            upload_status = gr.Textbox(label="上传状态", interactive=False)
                        kb_select_for_chat=gr.Dropdown(
                            label="为对话选择知识库",choices=current_kbs,
                            value=DEFAULT_KB if DEFAULT_KB in current_kbs else (
                                current_kbs[0] if current_kbs else None),visible=False  # 隐藏，仅用于同步
                        )

                        with gr.Column(scale=1, min_width=400):
                            with gr.Group(elem_id="kb-files-group"):
                                gr.Markdown("### 📋 知识库内容")
                                kb_files_list = gr.Markdown(
                                    value="选择知识库查看文件...",
                                    elem_classes="kb-files-list"
                                )
                        # 用于对话界面的知识库选择器
                        kb_select_for_chat = gr.Dropdown(
                            label="为对话选择知识库",
                            choices=current_kbs,
                            value=DEFAULT_KB if DEFAULT_KB in current_kbs else (
                                current_kbs[0] if current_kbs else None),
                            visible=False  # 隐藏，仅用于同步
                        )


            with gr.TabItem("对话交互"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ 对话设置")

                        kb_dropdown_chat = gr.Dropdown(
                            label="选择知识库进行对话",
                            choices=current_kbs,
                            value=DEFAULT_KB if DEFAULT_KB in current_kbs else (current_kbs[0] if current_kbs else None),
                        )
                        with gr.Row():
                            web_search_toggle = gr.Checkbox(
                                label="🌐 启用联网搜索",
                                value=True,
                                info="获取最新动态",
                                elem_classes="web-search-toggle"
                            )
                            table_format_toggle = gr.Checkbox(
                                label="📊 表格格式输出",
                                value=True,
                                info="使用Markdown表格展示结构化回答",
                                elem_classes="web-search-toggle"
                            )

                        multi_hop_toggle = gr.Checkbox(
                            label="🔄 启用多跳推理",
                            value=False,
                            info="使用高级多跳推理机制（较慢但更全面）",
                            elem_classes="multi-hop-toggle"
                        )

                        with gr.Accordion("显示检索进展", open=False):
                            search_results_output = gr.Markdown(
                                label="检索过程",
                                elem_id="search-results",
                                value="等待提交问题..."
                            )

                    with gr.Column(scale=3):
                        gr.Markdown("### 💬 对话历史")
                        chatbot = gr.Chatbot(
                            elem_id="chatbot",
                            label="对话历史",
                            height=550
                        )

                with gr.Row():
                    question_input = gr.Textbox(
                        label="输入医疗健康相关问题",
                        placeholder="例如：2型糖尿病的症状和治疗方法有哪些？",
                        lines=2,
                        elem_id="question-input"
                    )

                with gr.Row(elem_classes="submit-row"):
                    submit_btn = gr.Button("提交问题", variant="primary", elem_classes="submit-btn")
                    clear_btn = gr.Button("清空输入", variant="secondary")
                    clear_history_btn = gr.Button("清空对话历史", variant="secondary", elem_classes="clear-history-btn")

                # 状态显示框
                status_box = gr.HTML(
                    value='<div class="status-box status-processing">准备就绪，等待您的问题</div>',
                    visible=True
                )
                gr.Examples(
                    examples=[
                        ["2型糖尿病的症状和治疗方法有哪些？"],
                        ["高血压患者的日常饮食应该注意什么？"],
                        ["肺癌的早期症状和筛查方法是什么？"],
                        ["新冠肺炎后遗症有哪些表现？如何缓解？"],
                        ["儿童过敏性鼻炎的诊断标准和治疗方案有哪些？"]
                    ],
                    inputs=question_input,
                    label="示例问题（点击尝试）"
                )


    '''创建知识库并刷新'''
    def create_kb_and_refresh(kb_name):#创建知识库并刷新
        result=create_knowledge_base(kb_name,KB_BASE_DIR)
        kbs = get_knowledge_bases()
        return result, gr.update(choices=kbs, value=kb_name if "创建成功" in result else None), gr.update(choices=kbs,
                                                                                                          value=kb_name if "创建成功" in result else None)
    create_kb_btn.click(
        fn=create_kb_and_refresh,inputs=[new_kb_name],outputs=[kb_status, kb_dropdown, kb_dropdown_chat]##知识库状态,选择知识库,选择知识库进行对话
    ).then( fn=lambda: "",  inputs=[],   outputs=[new_kb_name] )


    '''# 刷新知识库列表'''
    def refresh_kb_list():
        kbs = get_knowledge_bases()
        print(kbs)
        # 更新两个下拉菜单
        return gr.update(choices=kbs, value=kbs[0] if kbs else None), gr.update(choices=kbs,
                                                                                value=kbs[0] if kbs else None)

    refresh_kb_btn.click(
        fn=refresh_kb_list,
        inputs=[],
        outputs=[kb_dropdown, kb_dropdown_chat]#选择知识库,选择知识库进行对话
    )

    '''删除知识库'''
    def delete_kb_and_refresh(kb_name):
        result = delete_knowledge_base(kb_name,DEFAULT_KB,KB_BASE_DIR)
        kbs = get_knowledge_bases()
        # 更新两个下拉菜单
        return result, gr.update(choices=kbs, value=kbs[0] if kbs else None), gr.update(choices=kbs,value=kbs[0] if kbs else None)


    delete_kb_btn.click(
        fn=delete_kb_and_refresh,
        inputs=[kb_dropdown],
        outputs=[kb_status, kb_dropdown, kb_dropdown_chat]
    ).then( fn=update_kb_files_list, inputs=[kb_dropdown],outputs=[kb_files_list]
    )##知识库状态,选择知识库,选择知识库进行对话,选择知识库查看文件


    ''' # 同步知识库选择 - 管理界面到对话界面'''
    def sync_kb_to_chat(kb_name):
        return gr.update(value=kb_name)
    # 知识库选择变化时 - 管理界面
    kb_dropdown.change(
        fn=on_kb_change,
        inputs=[kb_dropdown],
        outputs=[kb_status, kb_files_list]
    ).then(
        fn=sync_kb_to_chat,
        inputs=[kb_dropdown],
        outputs=[kb_dropdown_chat]
    )


    '''# 同步知识库选择 - 对话界面到管理界面'''
    def sync_chat_to_kb(kb_name):
        return gr.update(value=kb_name), update_kb_files_list(kb_name)

    # 知识库选择变化时 - 对话界面
    kb_dropdown_chat.change(
        fn=sync_chat_to_kb,
        inputs=[kb_dropdown_chat],
        outputs=[kb_dropdown, kb_files_list]
    )





    # 处理文件上传
    file_upload.upload(
        fn=process_upload_to_kb,
        inputs=[file_upload, kb_dropdown],
        outputs=[upload_status, kb_files_list]
    )

    # 清空输入按钮功能
    clear_btn.click(
        fn=lambda: "",
        inputs=[],
        outputs=[question_input]
    )


    # 清空对话历史按钮功能
    def clear_history():
        return [], []


    clear_history_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[chatbot, chat_history_state]
    )

    # 连接提交按钮
    submit_btn.click(
        fn=process_and_update_chat,
        ###输入，选择知识库，启用联网搜索，启用表格格式化，启用多跳，聊天历史
        inputs=[question_input, kb_dropdown_chat, web_search_toggle, table_format_toggle, multi_hop_toggle,
                chat_history_state],
        ##输出，状态，搜索结果
        outputs=[chatbot, status_box, search_results_output],
        queue=True
    ).then(
        fn=lambda: "",  # 清空输入框
        inputs=[],
        outputs=[question_input])
    # ).then(
    #     fn=lambda h: h,  # 更新state
    #     inputs=[chatbot],
    #     outputs=[chat_history_state]
    # )




if __name__ == '__main__':
    demo.launch(server_name='127.0.0.1',server_port=8888,share=True)