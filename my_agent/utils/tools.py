import sys
from langchain.tools import tool, BaseTool
from my_agent.config.database import db
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from my_agent.config.settings import load_llm
from .helpers import construir_clausula_where, formatar_resumo_filtros, safe_ident
from typing import Literal

sys.path.append("..")
from my_agent.models.request import QueryParams

toolkit = SQLDatabaseToolkit(db=db, llm=load_llm())
SQL_TOOLS: list[BaseTool] = toolkit.get_tools()


@tool("calcular_nps", description="Calcula o NPS (Net Promoter Score). Args: data_inicio (YYYY-MM-DD), data_fim (YYYY-MM-DD), agent (opcional, ex: 'Diane'), topic (opcional).")
def calcular_nps(params: QueryParams) -> str:
    """Calcula o NPS: (Promotores [4-5] - Detratores [1-2]) / Total * 100."""
    where_clauses = [f"Date BETWEEN '{params.data_inicio}' AND '{params.data_fim}'", "[Answered_Y_N] = 1", "[Satisfaction_rating] IS NOT NULL"]
    where_sql = construir_clausula_where(params.agent, params.topic, where_clauses)
    query = f"""
    SELECT ROUND(
        (CAST(COUNT(CASE WHEN [Satisfaction_rating] >= 4 THEN 1 END) AS FLOAT) - 
         CAST(COUNT(CASE WHEN [Satisfaction_rating] <= 2 THEN 1 END) AS FLOAT)) * 100.0 / 
        NULLIF(COUNT(*), 0),
        2
    ) AS nps
    FROM [01 Call-Center-Dataset]
    WHERE {where_sql}
    """
    resultado = db.run(query)
    filtros = formatar_resumo_filtros(params.data_inicio, params.data_fim, params.agent, params.topic)
    return f"{filtros}\nNPS: {resultado}"

@tool("calcular_tmo", description="Calcula o TMO (Tempo Médio Operacional) em HH:MM:SS. Args: data_inicio (YYYY-MM-DD), data_fim (YYYY-MM-DD), agent (opcional), topic (opcional).")
def calcular_tmo(params: QueryParams) -> str:
    """Calcula o TMO em formato 00:00:00."""
    where_clauses = [f"Date BETWEEN '{params.data_inicio}' AND '{params.data_fim}'", "[Answered_Y_N] = 1", "[AvgTalkDuration] IS NOT NULL"]
    where_sql = construir_clausula_where(params.agent, params.topic, where_clauses)
    query = f"""
    SELECT CONVERT(VARCHAR(8), DATEADD(SECOND, 
        CAST(AVG(CAST(DATEDIFF(SECOND, '00:00:00', [AvgTalkDuration]) AS FLOAT)) AS INT), 
        '00:00:00'), 108) AS tmo_formato
    FROM [01 Call-Center-Dataset]
    WHERE {where_sql}
    """
    resultado = db.run(query)
    filtros = formatar_resumo_filtros(params.data_inicio, params.data_fim, params.agent, params.topic)
    return f"{filtros}\nTMO (HH:MM:SS): {resultado}"

@tool("ligacoes_atendidas", description="Conta o total de ligações atendidas. Args: data_inicio (YYYY-MM-DD), data_fim (YYYY-MM-DD), agent (opcional), topic (opcional).")
def ligacoes_atendidas(params: QueryParams) -> str:
    """Retorna o total de ligações atendidas entre as datas."""
    where_clauses = [f"Date BETWEEN '{params.data_inicio}' AND '{params.data_fim}'", "[Answered_Y_N] = 1"]
    where_sql = construir_clausula_where(params.agent, params.topic, where_clauses)
    query = f"""
    SELECT COUNT(*) AS total_atendidas
    FROM [01 Call-Center-Dataset]
    WHERE {where_sql}
    """
    resultado = db.run(query)
    filtros = formatar_resumo_filtros(params.data_inicio, params.data_fim, params.agent, params.topic)
    return f"{filtros}\nTotal atendidas: {resultado}"

@tool("nps_por_agente", description="NPS agrupado por campo. Args: data_inicio, data_fim, topic (opcional), group_by ('Agent'|'Topic', padrão 'Agent').")
def nps_por_agente(params: QueryParams, group_by: Literal["Agent", "Topic"] = "Agent") -> str:
    group_col = safe_ident(group_by)
    where_clauses = [f"Date BETWEEN '{params.data_inicio}' AND '{params.data_fim}'","[Answered_Y_N] = 1","[Satisfaction_rating] IS NOT NULL"]
    where_sql = construir_clausula_where(params.agent, params.topic, where_clauses)
    query = f"""
    SELECT {group_col} AS grupo,
           ROUND(
             (CAST(COUNT(CASE WHEN [Satisfaction_rating] >= 4 THEN 1 END) AS FLOAT) -
              CAST(COUNT(CASE WHEN [Satisfaction_rating] <= 2 THEN 1 END) AS FLOAT)) * 100.0 /
             NULLIF(COUNT(*), 0), 2
           ) AS nps
    FROM [01 Call-Center-Dataset]
    WHERE {where_sql}
    GROUP BY {group_col}
    ORDER BY nps DESC
    """
    rows = db.run(query)
    return f"NPS por {group_by} ({params.data_inicio} a {params.data_fim}): {rows}"

@tool("tmo_por_agente", description="TMO médio por campo. Args: data_inicio, data_fim, topic (opcional), group_by ('Agent'|'Topic', padrão 'Agent').")
def tmo_por_agente(params: QueryParams, group_by: Literal["Agent", "Topic"] = "Agent") -> str:
    group_col = safe_ident(group_by)
    where_clauses = [f"Date BETWEEN '{params.data_inicio}' AND '{params.data_fim}'","[Answered_Y_N] = 1","[AvgTalkDuration] IS NOT NULL"]
    where_sql = construir_clausula_where(params.agent, params.topic, where_clauses)
    query = f"""
    SELECT {group_col} AS grupo,
           CONVERT(VARCHAR(8), DATEADD(SECOND,
               CAST(AVG(CAST(DATEDIFF(SECOND, '00:00:00', [AvgTalkDuration]) AS FLOAT)) AS INT),
               '00:00:00'), 108) AS tmo
    FROM [01 Call-Center-Dataset]
    WHERE {where_sql}
    GROUP BY {group_col}
    ORDER BY tmo ASC
    """
    rows = db.run(query)
    return f"TMO por {group_by} ({params.data_inicio} a {params.data_fim}): {rows}"

@tool("contatos_por_topico", description="Total de ligações agrupado. Args: data_inicio, data_fim, agent (opcional), group_by ('Topic'|'Agent', padrão 'Topic').")
def contatos_por_topico(params: QueryParams, group_by: Literal["Topic", "Agent"] = "Topic") -> str:
    group_col = safe_ident(group_by)
    where_clauses = [f"Date BETWEEN '{params.data_inicio}' AND '{params.data_fim}'","[Answered_Y_N] = 1"]
    where_sql = construir_clausula_where(params.agent, params.topic, where_clauses)
    query = f"""
    SELECT {group_col} AS grupo, COUNT(*) AS total
    FROM [01 Call-Center-Dataset]
    WHERE {where_sql}
    GROUP BY {group_col}
    ORDER BY total DESC
    """
    rows = db.run(query)
    return f"Contatos por {group_by} ({params.data_inicio} a {params.data_fim}): {rows}"

CUSTOM_TOOLS: list[BaseTool] = [
    ligacoes_atendidas, calcular_tmo, calcular_nps,
    nps_por_agente, tmo_por_agente, contatos_por_topico
]
ALL_TOOLS: list[BaseTool] = SQL_TOOLS + CUSTOM_TOOLS
