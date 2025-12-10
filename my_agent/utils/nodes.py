from typing import Dict, Any, Literal
from langgraph.graph import MessagesState, END
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from .tools import all_tools, run_query_tool, db

load_dotenv()

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-5.1-2025-11-13", temperature=0)

generate_query_system_prompt = f"""
Voce tem permissao para usar apenas SELECT consultas SQL para responder perguntas sobre os dados fornecidos.
Voce nao tem permissao para usar comandos como INSERT, UPDATE, DELETE ou qualquer outro comando que modifique os dados.
Você é um assistente de Call Center que responde perguntas sobre dados.
Dialeto SQL: {db.dialect}
Tabela: [01 Call-Center-Dataset]
Colunas: Call_Id, Agent, Date, Topic, Answered_Y_N, AvgTalkDuration, Satisfaction_rating

REGRAS DE PRIORIDADE (nessa ordem):
1. SEMPRE use 'calcular_nps' para NPS (aceita filtros: agent, topic)
2. SEMPRE use 'calcular_tmo' para TMO/tempo de atendimento (aceita filtros: agent, topic)
3. SEMPRE use 'ligacoes_atendidas' para total de ligações (aceita filtros: agent, topic)
4. Use 'sql_db_query' APENAS para consultas que não se encaixam nas ferramentas acima

IMPORTANTE:
- As ferramentas customizadas aceitam filtros opcionais (agent='Diane', topic='Streaming', etc)
- Se a pergunta menciona um agente ou tópico específico, passe como parâmetro
- NUNCA tente recriar lógica que já existe em uma ferramenta
- NUNCA retorne SQL para o usuário - sempre execute e retorne o resultado
"""

check_query_system_prompt = f"""
You are a SQL expert with a strong attention to detail.
Double check the {db.dialect} query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes,
just reproduce the original query.

You will call the appropriate tool to execute the query after running this check.
"""

def roteador(state: MessagesState) -> dict[str, Any]:
    """LLM pode escolher qualquer tool (custom ou SQL)"""
    llm_with_tools = llm.bind_tools(all_tools)
    system_message = {"role": "system", "content": generate_query_system_prompt}
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
    system_message = {"role": "system", "content": check_query_system_prompt}
    ai_message = next((m for m in reversed(state["messages"]) if hasattr(m, "tool_calls") and m.tool_calls), None)
    if not ai_message or ai_message.tool_calls[0]["name"] != "sql_db_query":
        return {"messages": []}
    
    tool_call = ai_message.tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
    resp = llm_with_tools.invoke([system_message, user_message])
    resp.id = ai_message.id
    return {"messages": [resp]}
