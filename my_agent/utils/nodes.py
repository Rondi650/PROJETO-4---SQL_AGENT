from typing import Any, Literal
from langgraph.graph import MessagesState, END
from my_agent.config.settings import llm
from my_agent.config.prompts import GENERATE_QUERY_SYSTEM_PROMPT, CHECK_QUERY_SYSTEM_PROMPT
from .tools import all_tools, run_query_tool

def roteador(state: MessagesState) -> dict[str, Any]:
    """LLM pode escolher qualquer tool (custom ou SQL)"""
    llm_with_tools = llm.bind_tools(all_tools)
    system_message = {"role": "system", "content": GENERATE_QUERY_SYSTEM_PROMPT}
    resp = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [resp]}

def should_continue(state: MessagesState) -> Literal[END, "tools", "valida_consulta"]:
    """Decide qual caminho seguir após o roteador"""
    last = state["messages"][-1]
    if not getattr(last, "tool_calls", None): 
        return END
    tool_name = last.tool_calls[0]["name"]
    return "valida_consulta" if tool_name == "sql_db_query" else "tools"

def valida_consulta(state: MessagesState) -> dict[str, Any]:
    """Valida queries SQL antes de executar"""
    system_message = {"role": "system", "content": CHECK_QUERY_SYSTEM_PROMPT}
    ai_message = next((m for m in reversed(state["messages"]) if hasattr(m, "tool_calls") and m.tool_calls), None)
    if not ai_message or ai_message.tool_calls[0]["name"] != "sql_db_query":
        return {"messages": []}
    
    tool_call = ai_message.tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
    resp = llm_with_tools.invoke([system_message, user_message])
    resp.id = ai_message.id
    return {"messages": [resp]}
