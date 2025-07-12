import asyncio
import os
from datetime import datetime
from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, AnyMessage
from langchain_core.runnables import RunnableLambda, Runnable, RunnableConfig
from langgraph.graph import add_messages
from langgraph.prebuilt import ToolNode
from langchain_community.tools.tavily_search import TavilySearchResults
TAVILY_API_KEY='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'
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
@tool
async def School(school_name:str,degree:str, parse_docstring=True):
    '''提取学校和学位操作 ：获取想申请目标学校名称和学位（本科，博士，硕士，研究生...）'''
    yield f'''申请的学校{school_name},成绩是{degree}'''
@tool
async def chat_round(his_school_name:str,major:str,GPA:str, parse_docstring=True):
    '''提取目前学校和GPA操作：
    (1) 您目前就读于国内哪个学校哪个专业？
    (2) 您当前的GPA是多少？'''
    yield f'''您目前就读于国内{his_school_name},专业是{major},当前的GPA{GPA}'''


async def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls

    return {
        "messages": [
            ToolMessage(
                content=f"错误： {repr(error)}\n 请修正你的错误。",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list, parse_docstring=True) -> dict:
    """
    Creates a tool node with fallback mechanisms.

    Args:
        tools (list): A list of tools to be used in the tool node.

    Returns:
        dict: A dictionary representing the tool node with fallback configurations.
    """
    return  ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("当前状态: ", current_state[-1])
    message = event.get("messages")
    # print('aaaaaaaaaa',message)
    if message:
        # print(message[1].additional_kwargs['tool_calls'])
        # print(100 * '-')
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (截断)"
            # print(msg_repr)
            _printed.add(message.id)
            return msg_repr
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("passenger_id", None)
            state = {**state, "user_info": passenger_id}
            result = self.runnable.invoke(state)

            # 如果LLM返回空响应，我们将重新提示它
            # 以获取实际响应。
            if result and not result.tool_calls and (
                    not result.content
                    or isinstance(result.content, list)
                    and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "请给出实际输出。")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
from langchain_core.tools import Tool
def main(new_history_list):
    TavilySearc=TavilySearchResults(max_results=1)
    llm = ChatOpenAI(model="gpt-4.1", base_url="https://api.302.ai/v1/chat/completions",
                     api_key="sk-gPl43py4bj6TN3mksIN18FPbRZXdHoV6i0XOAAshKFpanIb1")
    a = [
        Tool(name="add_one", func=School, description="提取学校和学位操作"),
        Tool(name="chat_round", func=chat_round, description="提取目前学校和GPA操作"),
    ]

    tools_=[TavilySearc,School,chat_round]
    tools = ToolNode(a).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一名留学主力。 "
                " 使用提供的工具提取需要申请的学校，学位 ，以及当前就读的学校和专业以及GPA "
                " 搜索时要坚持不懈 "
                " 如果搜索结果为空，请在放弃前扩大搜索范围。"
                "如果提问的问题不在工具中，请使用大模型和网络根据需求数据整理好输出"
           "如果目标申请学校和申请的学位和当前就读学校，专业以及当前GPA，根据这些信息做分析"
                "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
                "\nCurrent time: {time}.",
            ),
            ("placeholder", "{messages}"),
        ]
    ).partial(time=datetime.now)
    part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools_)
    builder = StateGraph(State)
    # 定义节点：这些节点完成工作
    builder.add_node("assistant", Assistant(part_1_assistant_runnable))
    builder.add_node("tools", create_tool_node_with_fallback(tools_))
    # 定义边：这些决定了控制流如何移动
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")
    from IPython.display import Image, display
    # 检查点使图保持其状态
    # 这是整个图的完整内存。
    memory = MemorySaver()
    part_1_graph = builder.compile(checkpointer=memory)


    config = {
        "configurable": {
            # passenger_id 用于我们的航班工具
            # 以获取用户的航班信息
            "passenger_id": "3442 587242",
            # 检查点通过 thread_id 访问
            "thread_id": '1234565',
        }
    }
    _printed=set()
    events = part_1_graph.stream(
        {"messages": ("user", new_history_list)}, config, stream_mode="values"
    )
    for event in events:
        a = _print_event(event, _printed)
    sp = a.split('Ai Message')[1].split('=')[-1:]
    s=''
    for i in sp:
        s+=i.strip()
    print(s)
    return (s)
main('博士')