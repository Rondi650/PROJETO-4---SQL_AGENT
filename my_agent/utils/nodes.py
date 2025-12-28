from typing import Literal
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langgraph.graph.state import RunnableConfig
from my_agent.config.settings import load_llm
from my_agent.config.prompts import GENERATE_QUERY_SYSTEM_PROMPT, CHECK_QUERY_SYSTEM_PROMPT
from .tools import ALL_TOOLS, SQL_TOOLS
from rich import print
from rich.markdown import Markdown


def roteador(state: MessagesState, config = RunnableConfig()) -> MessagesState:
    """LLM pode escolher qualquer tool (custom ou SQL)"""

    temperatura = config.get("configurable", {}).get("temperature", 0)
    print(Markdown(f"### Temperatura do LLM no roteador: {temperatura}"))
    
    llm_with_tools = load_llm(temperature=temperatura).bind_tools(ALL_TOOLS)

    system_message = SystemMessage(GENERATE_QUERY_SYSTEM_PROMPT)
    
    resp = llm_with_tools.invoke([system_message] + state["messages"])
    
    print(Markdown("---"))
    print('Config no roteador:')
    print(config)
    print(Markdown("---"))
    
    
        
    return {"messages": [resp]}

def should_continue(state: MessagesState) -> Literal["valida_consulta", "tools", "__end__"]:
    last = state["messages"][-1]
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return "__end__"
    tool_name = last.tool_calls[0]["name"]
    return "valida_consulta" if tool_name == "sql_db_query" else "tools"

def valida_consulta(state: MessagesState) -> MessagesState:
    system_message = SystemMessage(CHECK_QUERY_SYSTEM_PROMPT)
    last = state["messages"][-1]
    
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return {"messages": []}
    if last.tool_calls[0]["name"] != "sql_db_query":
        return {"messages": []}
    
    tool_call = last.tool_calls[0]
    user_message = HumanMessage(tool_call["args"]["query"])
    run_query_tool = next(t for t in SQL_TOOLS if t.name == "sql_db_query")
    llm_with_tools = load_llm().bind_tools([run_query_tool], tool_choice="any")
    resp = llm_with_tools.invoke([system_message, user_message])
    resp.id = last.id
    return {"messages": [resp]}
