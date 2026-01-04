"""
Exemplo simples de uso com controle de acesso
"""
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from typing import Literal

from my_agent.utils.security_nodes import add_sql_filter
from my_agent.utils.nodes import roteador, should_continue, valida_consulta
from my_agent.utils.tools import ALL_TOOLS


def create_simple_secure_agent():
    """Cria agente com controle de acesso básico"""
    tools_node = ToolNode(ALL_TOOLS, name="tools")
    
    builder = StateGraph(MessagesState)
    
    # Nós
    builder.add_node("roteador", roteador)
    builder.add_node("add_sql_filter", add_sql_filter)  # Novo nó
    builder.add_node("valida_consulta", valida_consulta)
    builder.add_node("tools", tools_node)
    
    # Fluxo
    builder.add_edge(START, "roteador")
    
    # Roteamento condicional modificado
    def should_continue_secure(state: MessagesState) -> Literal["add_sql_filter", "tools", "__end__"]:
        last = state["messages"][-1]
        if not hasattr(last, "tool_calls") or not last.tool_calls:
            return "__end__"
        tool_name = last.tool_calls[0]["name"]
        return "add_sql_filter" if tool_name == "sql_db_query" else "tools"
    
    builder.add_conditional_edges("roteador", should_continue_secure, ["add_sql_filter", "tools", "__end__"])
    builder.add_edge("add_sql_filter", "valida_consulta")
    builder.add_edge("valida_consulta", "tools")
    builder.add_edge("tools", "roteador")
    
    return builder.compile()


# Criar agente
secure_agent = create_simple_secure_agent()


# ============ EXEMPLO DE USO ============
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTE: Usuário JAIRO (acesso apenas operação X)")
    print("="*60 + "\n")
    
    config = RunnableConfig(
        configurable={
            "thread_id": "test_001",
            "user_id": "Jairo"  # Mudar para "Maria" ou "Admin" para testar
        }
    )
    
    pergunta = HumanMessage(
        content="Mostre o total de ligações atendidas em janeiro de 2024"
    )
    
    result = secure_agent.invoke(
        {"messages": [pergunta]},
        config=config
    )
    
    print("\n📊 Resposta:")
    print(result["messages"][-1].content)
    print("\n" + "="*60)
