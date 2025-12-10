from langchain.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Inicializar conexões
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-5.1-2025-11-13", temperature=0)

db = SQLDatabase.from_uri(
    "mssql+pyodbc://localhost/Teste_CallCenter?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
    include_tables=["01 Call-Center-Dataset"],
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = toolkit.get_tools()

@tool("calcular_nps", description="Calcula o NPS (Net Promoter Score). Args: data_inicio (YYYY-MM-DD), data_fim (YYYY-MM-DD), agent (opcional, ex: 'Diane'), topic (opcional).")
def calcular_nps(data_inicio: str, data_fim: str, agent: str = None, topic: str = None) -> str:
    """
    Calcula o NPS: (Promotores [4-5] - Detratores [1-2]) / Total * 100.
    
    Args:
        data_inicio: Data inicial em formato YYYY-MM-DD
        data_fim: Data final em formato YYYY-MM-DD
        agent: Nome do agente (opcional, ex: 'Diane', 'Becky')
        topic: Tópico (opcional, ex: 'Streaming', 'Technical Support')
    """
    where_clauses = [f"Date BETWEEN '{data_inicio}' AND '{data_fim}'", "[Answered_Y_N] = 1", "[Satisfaction_rating] IS NOT NULL"]
    
    if agent:
        where_clauses.append(f"[Agent] = '{agent}'")
    if topic:
        where_clauses.append(f"[Topic] = '{topic}'")
    
    where_sql = " AND ".join(where_clauses)
    
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
    
    filtros = f"Período: {data_inicio} a {data_fim}"
    if agent:
        filtros += f", Agente: {agent}"
    if topic:
        filtros += f", Tópico: {topic}"
    
    return f"{filtros}\nNPS: {resultado}"

@tool("calcular_tmo", description="Calcula o TMO (Tempo Médio Operacional) em HH:MM:SS. Args: data_inicio (YYYY-MM-DD), data_fim (YYYY-MM-DD), agent (opcional), topic (opcional).")
def calcular_tmo(data_inicio: str, data_fim: str, agent: str = None, topic: str = None) -> str:
    """Calcula o TMO em formato 00:00:00."""
    where_clauses = [f"Date BETWEEN '{data_inicio}' AND '{data_fim}'", "[Answered_Y_N] = 1", "[AvgTalkDuration] IS NOT NULL"]
    
    if agent:
        where_clauses.append(f"[Agent] = '{agent}'")
    if topic:
        where_clauses.append(f"[Topic] = '{topic}'")
    
    where_sql = " AND ".join(where_clauses)
    
    query = f"""
    SELECT CONVERT(VARCHAR(8), DATEADD(SECOND, 
        CAST(AVG(CAST(DATEDIFF(SECOND, '00:00:00', [AvgTalkDuration]) AS FLOAT)) AS INT), 
        '00:00:00'), 108) AS tmo_formato
    FROM [01 Call-Center-Dataset]
    WHERE {where_sql}
    """
    resultado = db.run(query)
    
    filtros = f"Período: {data_inicio} a {data_fim}"
    if agent:
        filtros += f", Agente: {agent}"
    if topic:
        filtros += f", Tópico: {topic}"
    
    return f"{filtros}\nTMO (HH:MM:SS): {resultado}"

@tool("ligacoes_atendidas", description="Conta o total de ligações atendidas. Args: data_inicio (YYYY-MM-DD), data_fim (YYYY-MM-DD), agent (opcional), topic (opcional).")
def ligacoes_atendidas(data_inicio: str, data_fim: str, agent: str = None, topic: str = None) -> str:
    """Retorna o total de ligações atendidas entre as datas."""
    where_clauses = [f"Date BETWEEN '{data_inicio}' AND '{data_fim}'", "[Answered_Y_N] = 1"]
    
    if agent:
        where_clauses.append(f"[Agent] = '{agent}'")
    if topic:
        where_clauses.append(f"[Topic] = '{topic}'")
    
    where_sql = " AND ".join(where_clauses)
    
    query = f"""
    SELECT COUNT(*) AS total_atendidas
    FROM [01 Call-Center-Dataset]
    WHERE {where_sql}
    """
    resultado = db.run(query)
    
    filtros = f"Período: {data_inicio} a {data_fim}"
    if agent:
        filtros += f", Agente: {agent}"
    if topic:
        filtros += f", Tópico: {topic}"
    
    return f"{filtros}\nTotal atendidas: {resultado}"

# Exportar todas as tools
custom_tools = [ligacoes_atendidas, calcular_tmo, calcular_nps]
all_tools = sql_tools + custom_tools
run_query_tool = next(t for t in sql_tools if t.name == "sql_db_query")
