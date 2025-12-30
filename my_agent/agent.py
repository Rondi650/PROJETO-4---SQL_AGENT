from langgraph.graph import StateGraph, START, MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from .utils import (
    ALL_TOOLS,
    roteador,
    should_continue,
    valida_consulta
)

def create_agent():
    """Cria e compila o grafo do agente"""
    tools_node = ToolNode(ALL_TOOLS, name="tools")
    
    builder = StateGraph(MessagesState)
    builder.add_node("roteador", roteador)
    builder.add_node("tools", tools_node) # execucao ocorre apenas aqui
    builder.add_node("valida_consulta", valida_consulta)
    
    builder.add_edge(START, "roteador")
    builder.add_conditional_edges("roteador", should_continue, ["valida_consulta", "tools", "__end__"])
    builder.add_edge("tools", "roteador")
    builder.add_edge("valida_consulta", "tools")
    
    checkpointer = InMemorySaver()
    agent = builder.compile(checkpointer=checkpointer)
    
    return agent

# Criar instância do agente
agent = create_agent()
