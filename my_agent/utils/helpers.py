
'''Funções auxiliares para construção de cláusulas SQL e formatação de resumos.'''

def construir_clausula_where(agent: str = None, topic: str = None, where_clauses: list[str] = None) -> str:
    '''
    Args:
        agent (str, opcional): Nome do agente.
        topic (str, opcional): Tópico da chamada.
        where_clauses (list[str]): Lista inicial de cláusulas WHERE.
        
    Returns:
        str: Cláusula WHERE completa.
    '''
    if agent:
        where_clauses.append(f"[Agent] = '{agent}'")
    if topic:
        where_clauses.append(f"[Topic] = '{topic}'")
    
    where_sql = " AND ".join(where_clauses)
    return where_sql

def formatar_resumo_filtros(data_inicio: str, data_fim: str, agent: str = None, topic: str = None) -> str:
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
