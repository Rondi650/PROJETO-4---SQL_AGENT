from typing import Any
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from my_agent.config.settings import llm
from my_agent.config.prompts import GENERATE_QUERY_SYSTEM_PROMPT, CHECK_QUERY_SYSTEM_PROMPT
from .tools import all_tools, sql_tools


def roteador(state: MessagesState) -> dict[str, Any]:
    """LLM pode escolher qualquer tool (custom ou SQL)"""
    llm_with_tools = llm.bind_tools(all_tools)
    system_message = {"role": "system", "content": GENERATE_QUERY_SYSTEM_PROMPT}
    resp = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [resp]}

def should_continue(state: MessagesState) -> str:
    """Decide qual caminho seguir após o roteador"""
    last = state["messages"][-1]
    
    # Verifica se é AIMessage antes de acessar tool_calls
    """
    ## Tabela verdade: `isinstance(last, AIMessage)`

    | `last` é...   | `isinstance(last, AIMessage)` | `not isinstance(last, AIMessage)` |
    |---------------|-------------------------------|-----------------------------------|
    | AIMessage     | True                          | False                             |
    | HumanMessage  | False                         | True                              |
    | ToolMessage   | False                         | True                              |
    | SystemMessage | False                         | True                              |
    """
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return END

    '''
    Tools customizadas (NPS, TMO, ligações) → vão direto para "tools"
    "calcular_nps"        → "tools"
    "calcular_tmo"        → "tools"
    "ligacoes_atendidas"  → "tools"

     Query SQL bruta → precisa validar antes → vai para "valida_consulta"
    "sql_db_query"        → "valida_consulta"
    '''
    tool_name = last.tool_calls[0]["name"]
    return "valida_consulta" if tool_name == "sql_db_query" else "tools"

def valida_consulta(state: MessagesState) -> dict[str, Any]:
    """Valida queries SQL antes de executar"""
    system_message = {"role": "system", "content": CHECK_QUERY_SYSTEM_PROMPT}
    
    # ✅ Pega a última mensagem (mesma lógica de should_continue)
    last = state["messages"][-1]
    
    # Verifica se é AIMessage com tool_calls
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return {"messages": []}
    
    # Verifica se a tool chamada é sql_db_query
    if last.tool_calls[0]["name"] != "sql_db_query":
        return {"messages": []}
    
    tool_call = last.tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    run_query_tool = next(t for t in sql_tools if t.name == "sql_db_query")
    llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
    resp = llm_with_tools.invoke([system_message, user_message])
    resp.id = last.id
    return {"messages": [resp]}
