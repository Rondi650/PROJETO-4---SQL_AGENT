
'''Funções auxiliares para construção de cláusulas SQL e formatação de resumos.'''

def safe_ident(name: str) -> str:
    """
    Args:
        name (str): Nome do identificador (coluna, tabela, etc.)
        
    Returns:
        str: Nome seguro para uso em consultas SQL.
    """
    name = name.strip()
    return name if (name.startswith("[") and name.endswith("]")) else f"[{name}]"

def construir_clausula_where(agent: str | None = None, topic: str | None = None, where_clauses: list[str] | None = None) -> str:
    '''
    Args:
        agent (str, opcional): Nome do agente.
        topic (str, opcional): Tópico da chamada.
        where_clauses (list[str]): Lista inicial de cláusulas WHERE.
        
    Returns:
        str: Cláusula WHERE completa.
    '''
    if where_clauses is None:
        where_clauses = []
    if agent:
        where_clauses.append(f"[Agent] = '{agent}'")
    if topic:
        where_clauses.append(f"[Topic] = '{topic}'")
    
    where_sql = " AND ".join(where_clauses)
    return where_sql

def formatar_resumo_filtros(data_inicio: str, data_fim: str, agent: str | None = None, topic: str | None = None) -> str:
    '''
    Args:
        data_inicio (str): Data de início no formato 'YYYY-MM-DD'.
        data_fim (str): Data de fim no formato 'YYYY-MM-DD'.
        agent (str, opcional): Nome do agente.
        topic (str, opcional): Tópico da chamada.
        
    Returns:
        str: Resumo dos filtros aplicados.
    '''
    filtros = f"Período: {data_inicio} a {data_fim}"
    if agent:
        filtros += f", Agente: {agent}"
    if topic:
        filtros += f", Tópico: {topic}"
    return filtros
