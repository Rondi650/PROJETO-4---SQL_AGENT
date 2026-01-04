"""
Nós simples para controle de acesso
"""
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage
from my_agent.config.user_permissions import get_user_operations


def add_sql_filter(state: MessagesState, config = None) -> MessagesState:
    """
    Adiciona filtro de operações permitidas à query SQL
    """
    # Pegar user_id do config
    user_id = config.get("configurable", {}).get("user_id", "guest") if config else "guest"
    allowed_ops = get_user_operations(user_id)
    
    # Se não há tool_calls ou usuário tem acesso total, não faz nada
    last = state["messages"][-1]
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return {}
    
    if allowed_ops is None:  # Acesso total
        return {}
    
    if not allowed_ops:  # Sem permissão
        return {
            "messages": [AIMessage(content=f"❌ Usuário '{user_id}' não tem permissões configuradas.")]
        }
    
    # Processar apenas queries SQL
    tool_call = last.tool_calls[0]
    if tool_call["name"] != "sql_db_query":
        return {}
    
    # Adicionar filtro WHERE à query
    original_query = tool_call["args"].get("query", "")
    operations_str = ", ".join([f"'{op}'" for op in allowed_ops])
    filter_clause = f"[Operation] IN ({operations_str})"
    
    # Injetar filtro (método simples)
    if "WHERE" in original_query.upper():
        filtered_query = original_query.replace("WHERE", f"WHERE ({filter_clause}) AND (", 1) + ")"
    else:
        # Adicionar WHERE antes de GROUP BY, ORDER BY, etc
        for keyword in ["GROUP BY", "ORDER BY", "LIMIT"]:
            if keyword in original_query.upper():
                pos = original_query.upper().find(keyword)
                filtered_query = original_query[:pos] + f"\nWHERE {filter_clause}\n" + original_query[pos:]
                break
        else:
            filtered_query = original_query + f"\nWHERE {filter_clause}"
    
    # Atualizar tool_call
    new_tool_call = tool_call.copy()
    new_tool_call["args"]["query"] = filtered_query
    new_message = last.copy()
    new_message.tool_calls = [new_tool_call]
    
    print(f"🔒 Filtro aplicado para {user_id}: operações {allowed_ops}")
    return {"messages": [new_message]}
