from typing import Literal
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from my_agent.config.settings import llm
from my_agent.config.prompts import GENERATE_QUERY_SYSTEM_PROMPT, CHECK_QUERY_SYSTEM_PROMPT
from .tools import CUSTOM_TOOLS


def roteador(state: MessagesState) -> MessagesState:
    """LLM pode escolher qualquer tool (custom ou SQL)"""
    llm_with_tools = llm.bind_tools(CUSTOM_TOOLS)
    system_message = SystemMessage(GENERATE_QUERY_SYSTEM_PROMPT)
    
    resp = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [resp]}

def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return "__end__"
    return "tools"
