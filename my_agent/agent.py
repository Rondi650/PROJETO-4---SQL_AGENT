from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from .utils import (
    CUSTOM_TOOLS,
    roteador,
    should_continue,
)

def create_agent():
    """Cria e compila o grafo do agente"""
    tools_node = ToolNode(CUSTOM_TOOLS, name="tools")
    
    builder = StateGraph(MessagesState)
    builder.add_node("roteador", roteador)
    builder.add_node("tools", tools_node) # execucao ocorre apenas aqui)
    
    builder.add_edge(START, "roteador")
    builder.add_conditional_edges("roteador", should_continue, ["tools", "__end__"])
    builder.add_edge("tools", "roteador")
    
    checkpointer = InMemorySaver()
    agent = builder.compile(checkpointer=checkpointer)
    
    return agent

# Criar instância do agente
agent = create_agent()
