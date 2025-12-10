# SQL Agent - Documentação Completa

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Projeto](#arquitetura-do-projeto)
3. [Estrutura de Diretórios](#estrutura-de-diretórios)
4. [Componentes Principais](#componentes-principais)
5. [Fluxo de Execução](#fluxo-de-execução)
6. [Configuração e Instalação](#configuração-e-instalação)
7. [Como Usar](#como-usar)
8. [API REST](#api-rest)
9. [Ferramentas Disponíveis](#ferramentas-disponíveis)
10. [Prompts do Sistema](#prompts-do-sistema)
11. [Modelos de Dados](#modelos-de-dados)

---

## 🎯 Visão Geral

**SQL Agent** é um agente inteligente baseado em IA (LangGraph + LangChain + GPT) que interpreta perguntas em linguagem natural e as converte em consultas SQL ou usa ferramentas customizadas para análise de dados de Call Center.

### Principais Características

- 🤖 **Agente Inteligente**: Usa GPT para compreender perguntas em português
- 🔍 **Roteamento Inteligente**: Decide automaticamente qual tool utilizar
- ✅ **Validação de Queries**: Valida consultas SQL antes de executar
- 📊 **Métricas de Call Center**: KPIs prontos (NPS, TMO, Ligações Atendidas)
- 🔌 **API REST**: Endpoint FastAPI para integração
- 💾 **Persistência**: Mantém histórico de conversas com InMemorySaver

---

## 🏗️ Arquitetura do Projeto

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI (main.py)                      │
│                    POST /chat endpoint                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Agent                           │
│                   (agent.py)                                │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │              │              │                      │    │
│  ▼              ▼              ▼                      ▼    │
│ START → ROTEADOR → should_continue (decisão)               │
│  │                                                          │
│  ├─→ TOOLS (custom ou sql_db_query)                        │
│  │                                                          │
│  └─→ VALIDA_CONSULTA (apenas para sql_db_query)           │
└─────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────────┐    ┌────────────────────────┐
│  Custom Tools        │    │   SQL Database         │
│  - calcular_nps      │    │   (MSSQL - CallCenter) │
│  - calcular_tmo      │    │                        │
│  - ligacoes_atendidas│    │   01 Call-Center-     │
└──────────────────────┘    │      Dataset          │
                            └────────────────────────┘
```

---

## 📁 Estrutura de Diretórios

```
PROJETO 4 - SQL_AGENT/
├── main.py                          # Aplicação FastAPI principal
├── pyproject.toml                   # Dependências do projeto
├── langgraph.json                   # Configuração LangGraph
│
├── my_agent/
│   ├── __init__.py                  # Exporta agent e create_agent
│   ├── agent.py                     # Criação e compilação do grafo
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py              # Conexão MSSQL
│   │   ├── settings.py              # Configuração OpenAI LLM
│   │   └── prompts.py               # Prompts do sistema (GENERATE e CHECK)
│   │
│   ├── models/
│   │   ├── request.py               # Modelos Pydantic de entrada
│   │   └── response.py              # Modelos Pydantic de saída
│   │
│   └── utils/
│       ├── __init__.py              # Exportações
│       ├── tools.py                 # Definição das ferramentas
│       ├── nodes.py                 # Nós do grafo (roteador, validação)
│       └── helpers.py               # Funções auxiliares
```

---

## 🔧 Componentes Principais

### 1. **agent.py** - Orquestrador Principal

```python
def create_agent() -> CompiledStateGraph
```

Cria o grafo de estados LangGraph com:
- **Nós**: `roteador`, `tools`, `valida_consulta`
- **Arestas**: Fluxo de execução condicional
- **Checkpointer**: InMemorySaver para manter histórico

### 2. **nodes.py** - Processadores de Lógica

#### `roteador(state: MessagesState) -> dict`
- Recebe mensagens do usuário
- Vincula ferramentas disponíveis ao LLM
- Invoca GPT com GENERATE_QUERY_SYSTEM_PROMPT
- Retorna resposta com tool_calls

#### `should_continue(state: MessagesState) -> str`
- Decide o próximo passo baseado na última mensagem
- Se `AIMessage` com `tool_calls`:
  - `"valida_consulta"` se tool é `sql_db_query`
  - `"tools"` para ferramentas customizadas
- Se não há `tool_calls`: `END` (conversação termina)

#### `valida_consulta(state: MessagesState) -> dict`
- Executa apenas para `sql_db_query`
- Valida SQL com CHECK_QUERY_SYSTEM_PROMPT
- Detecta erros comuns (NOT IN with NULL, UNION vs UNION ALL, etc)
- Executa query corrigida

### 3. **tools.py** - Ferramentas Disponíveis

#### **Ferramentas Customizadas**

```python
@tool("calcular_nps")
def calcular_nps(params: QueryParams) -> str
```
- **Descrição**: Calcula NPS (Net Promoter Score)
- **Fórmula**: `(Promotores[4-5] - Detratores[1-2]) / Total * 100`
- **Parâmetros**: 
  - `data_inicio` (obrigatório): YYYY-MM-DD
  - `data_fim` (obrigatório): YYYY-MM-DD
  - `agent` (opcional): Nome do agente
  - `topic` (opcional): Tópico da chamada

```python
@tool("calcular_tmo")
def calcular_tmo(params: QueryParams) -> str
```
- **Descrição**: Calcula TMO (Tempo Médio Operacional)
- **Retorno**: Formato HH:MM:SS
- **Parâmetros**: Mesmos do NPS

```python
@tool("ligacoes_atendidas")
def ligacoes_atendidas(params: QueryParams) -> str
```
- **Descrição**: Conta total de ligações atendidas
- **Parâmetros**: Mesmos do NPS

#### **Ferramentas do LangChain**
- `sql_db_query`: Executa qualquer query SQL (após validação)
- `sql_db_list_tables`: Lista tabelas disponíveis
- `sql_db_schema`: Retorna schema de uma tabela

### 4. **helpers.py** - Funções Auxiliares

```python
def construir_clausula_where(
    agent: str | None = None,
    topic: str | None = None,
    where_clauses: list[str] | None = None
) -> str
```
Constrói cláusula WHERE dinâmica com filtros opcionais.

```python
def formatar_resumo_filtros(
    data_inicio: str,
    data_fim: str,
    agent: str | None = None,
    topic: str | None = None
) -> str
```
Formata resumo legível dos filtros aplicados.

---

## 🔄 Fluxo de Execução

### Cenário 1: Pergunta sobre NPS

```
Usuário: "Qual o NPS de Diane em 2025-01-01 a 2025-01-31?"
                    ↓
         [START] → [ROTEADOR]
         GPT identifica: calcular_nps
                    ↓
         [should_continue] 
         Retorna: "tools" (não é sql_db_query)
                    ↓
              [TOOLS NODE]
         Executa: calcular_nps(
             data_inicio='2025-01-01',
             data_fim='2025-01-31',
             agent='Diane'
         )
                    ↓
         Retorna ao [ROTEADOR] com resultado
                    ↓
              [END]
         Resposta: "Período: 2025-01-01 a 2025-01-31, Agente: Diane\nNPS: 45.23"
```

### Cenário 2: Pergunta com SQL Bruto

```
Usuário: "Qual agente tem mais chamadas?"
                    ↓
         [START] → [ROTEADOR]
         GPT identifica: sql_db_query
         Query: SELECT TOP 1 Agent, COUNT(*) as total...
                    ↓
         [should_continue]
         Retorna: "valida_consulta" (é sql_db_query)
                    ↓
         [VALIDA_CONSULTA]
         Valida SQL com CHECK_QUERY_SYSTEM_PROMPT
         Se OK: passa para [TOOLS]
         Se erro: reescreve query
                    ↓
              [TOOLS NODE]
         Executa: sql_db_query(query=...)
                    ↓
         Retorna ao [ROTEADOR] com resultado
                    ↓
              [END]
         Resposta: Resultado tabulado da query
```

### Cenário 3: Conversação Sem Ferramentas

```
Usuário: "Olá, como você funciona?"
                    ↓
         [START] → [ROTEADOR]
         GPT responde diretamente
         AIMessage SEM tool_calls
                    ↓
         [should_continue]
         if not last.tool_calls: return END
                    ↓
              [END]
         Resposta: "Eu sou um assistente de Call Center..."
```

---

## ⚙️ Configuração e Instalação

### Pré-requisitos

- Python 3.13.5
- SQL Server com banco de dados (driver ODBC instalado)
- Chave API OpenAI

### Passos de Instalação

#### 1. Criar Ambiente Virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### 2. Instalar Dependências

```powershell
pip install -r requirements.txt
```

Ou via `pyproject.toml`:

```powershell
pip install -e .
```

#### 3. Configurar Variáveis de Ambiente

Criar arquivo `.env`:

```env
OPENAI_API_KEY=sk-your-key-here
```

#### 4. Verificar Conexão com SQL Server

```python
from my_agent.config.database import db
print(db.get_table_info())  # Deve retornar schema da tabela
```

#### 5. Testar Agente Localmente

```python
from my_agent import agent

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Qual o NPS?"}]},
    config={"configurable": {"thread_id": "test_1"}}
)
```

---

## 🚀 Como Usar

### Opção 1: Teste Local (Python)

```python
from my_agent import agent
from pprint import pprint

pergunta = "Qual o NPS de Diane em janeiro de 2025?"

resultado = agent.invoke(
    {"messages": [{"role": "user", "content": pergunta}]},
    config={"configurable": {"thread_id": "conversation_1"}}
)

print(resultado["messages"][-1].content)
```

### Opção 2: Streaming (Python)

```python
from my_agent import agent

pergunta = "Quantas ligações foram atendidas?"

for step in agent.stream(
    {"messages": [{"role": "user", "content": pergunta}]},
    config={"configurable": {"thread_id": "stream_test"}},
    stream_mode="values"
):
    print(step["messages"][-1])
```

### Opção 3: API REST (FastAPI)

#### Iniciar Servidor

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Fazer Requisição

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Qual o NPS de Diane?"}'
```

#### Resposta

```json
{
  "response": "Período: 2025-01-01 a 2025-01-31, Agente: Diane\nNPS: 45.23",
  "data_hora": "2025-01-10T14:30:00",
  "thread_id": "api_conversation"
}
```

---

## 📡 API REST

### Documentação Interativa

Após iniciar o servidor, acesse:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoints

#### `POST /chat`

Envia uma pergunta e recebe resposta do agente.

**Request Body**:
```json
{
  "pergunta": "Qual o NPS?"
}
```

**Response** (200 OK):
```json
{
  "response": "string (resposta do agente)",
  "data_hora": "2025-01-10T14:30:00",
  "thread_id": "string (identificador da conversa)"
}
```

**Status Codes**:
- `200`: Sucesso
- `422`: Validação falhou (pergunta vazia ou > 200 caracteres)

---

## 🛠️ Ferramentas Disponíveis

### Hierarquia de Seleção

A ordem de prioridade para escolha de ferramentas é:

```
1. NPS (calcular_nps)
   ↓ (se pergunta menciona "NPS" ou "satisfação")
2. TMO (calcular_tmo)
   ↓ (se pergunta menciona "tempo" ou "TMO")
3. Ligações (ligacoes_atendidas)
   ↓ (se pergunta menciona "chamadas" ou "atendidas")
4. SQL Genérico (sql_db_query)
   ↓ (para qualquer outra consulta)
```

### Prompts que Acionam Cada Ferramenta

#### calcular_nps
- "Qual o NPS?"
- "Qual a satisfação?"
- "NPS do agente X?"
- "Como é o NPS por tópico?"

#### calcular_tmo
- "Qual o tempo médio?"
- "Qual o TMO?"
- "Tempo de atendimento do agente?"
- "Quanto tempo leva em média?"

#### ligacoes_atendidas
- "Quantas ligações?"
- "Total de chamadas?"
- "Ligações atendidas?"
- "Qual o volume?"

#### sql_db_query
- "Qual agente fez mais chamadas?"
- "Quais são os tópicos?"
- "Ranking de agentes?"
- Qualquer pergunta não coberta acima

---

## 💬 Prompts do Sistema

### GENERATE_QUERY_SYSTEM_PROMPT

Define as regras para o LLM gerar queries/tool calls:

```
✅ Permitido: SELECT queries apenas
❌ Não permitido: INSERT, UPDATE, DELETE

TABELA: [01 Call-Center-Dataset]
COLUNAS: Call_Id, Agent, Date, Topic, Answered_Y_N, 
         AvgTalkDuration, Satisfaction_rating

REGRAS:
1. SEMPRE use 'calcular_nps' para NPS
2. SEMPRE use 'calcular_tmo' para TMO
3. SEMPRE use 'ligacoes_atendidas' para total de ligações
4. Use 'sql_db_query' APENAS para consultas não cobertas

DICA: Ferramentas customizadas aceitam filtros 
(agent='Diane', topic='Streaming', etc)
```

### CHECK_QUERY_SYSTEM_PROMPT

Valida queries antes de executar:

```
Verifica:
- ✓ NOT IN com NULL values
- ✓ UNION vs UNION ALL
- ✓ BETWEEN para ranges
- ✓ Type mismatch em predicados
- ✓ Identifiers entre aspas
- ✓ Número correto de argumentos de funções
- ✓ Casts para tipo correto
- ✓ Colunas corretas em JOINs

Se houver erro: reescreve
Se OK: reproduz original
```

---

## 📊 Modelos de Dados

### Request Models (Entrada)

#### `PerguntaModel`
```python
class PerguntaModel(BaseModel):
    pergunta: str  # Minimo: 1, Máximo: 200 caracteres
```

#### `QueryParams`
```python
class QueryParams(BaseModel):
    agent: str | None = None           # Ex: "Diane"
    topic: str | None = None           # Ex: "Streaming"
    data_inicio: str                    # Obrigatório: YYYY-MM-DD
    data_fim: str                       # Obrigatório: YYYY-MM-DD
```

### Response Models (Saída)

#### `RespostaModel`
```python
class RespostaModel(BaseModel):
    response: str                       # Resposta do agente
    data_hora: datetime                 # Timestamp da resposta
    thread_id: str                      # ID da conversa
```

---

## 🗄️ Banco de Dados

### Conexão

**Driver**: MSSQL via ODBC  
**Autenticação**: Trusted Connection (Windows Auth)

```python
mssql+pyodbc://localhost/Teste_CallCenter?
    driver=ODBC+Driver+17+for+SQL+Server&
    trusted_connection=yes
```

### Tabela Principal

**Nome**: `01 Call-Center-Dataset`

**Schema**:
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `Call_Id` | INT | ID único da chamada |
| `Agent` | VARCHAR | Nome do agente |
| `Date` | DATE | Data da chamada |
| `Topic` | VARCHAR | Tópico da chamada |
| `Answered_Y_N` | INT | 1=Atendida, 0=Não atendida |
| `AvgTalkDuration` | TIME | Duração média da chamada |
| `Satisfaction_rating` | INT | 1-5 (satisfação) |

---

## 🔍 Exemplos de Uso Completo

### Exemplo 1: Consultar NPS com Filtros

```python
from my_agent import agent

# LLM automaticamente interpreta e chama calcular_nps
result = agent.invoke(
    {"messages": [
        {"role": "user", "content": "Qual o NPS do agente Diane para Streaming?"}
    ]},
    config={"configurable": {"thread_id": "nps_diane"}}
)

print(result["messages"][-1].content)
# Output: Período: 2025-01-01 a 2025-01-31, Agente: Diane, Tópico: Streaming
#         NPS: 42.50
```

### Exemplo 2: Comparar Métricas

```python
# Pergunta complexa que requer SQL
result = agent.invoke(
    {"messages": [
        {"role": "user", "content": 
         "Liste os 5 agentes com maior TMO em janeiro/2025"}
    ]},
    config={"configurable": {"thread_id": "top5_tmo"}}
)

# LLM vai usar sql_db_query, passar por validação
# e retornar resultado tabulado
print(result["messages"][-1].content)
```

### Exemplo 3: Análise Exploratória

```python
# Conversação multi-turno
messages = [
    {"role": "user", "content": "Qual o NPS geral?"}
]

for turn in range(3):
    result = agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": "exploration"}}
    )
    
    last_msg = result["messages"][-1]
    messages.append({"role": "assistant", "content": last_msg.content})
    
    print(f"Turn {turn+1}: {last_msg.content}\n")
    
    # Usuário adiciona próxima pergunta
    user_input = input("Próxima pergunta: ")
    messages.append({"role": "user", "content": user_input})
```

---

## 🐛 Troubleshooting

### "ODBC Driver 17 not found"

```powershell
# Instalar driver no Windows
# Download: https://docs.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### "OPENAI_API_KEY not set"

```powershell
# Adicionar ao .env
OPENAI_API_KEY=sk-...

# Ou via variável de ambiente
$env:OPENAI_API_KEY="sk-..."
```

### "Connection refused: localhost"

```python
# Verificar conexão SQL Server
from my_agent.config.database import db
try:
    print(db.get_table_info())
except Exception as e:
    print(f"Erro: {e}")
```

### "Tool not called correctly"

Verificar se o LLM está chamando as ferramentas corretamente:

```python
result = agent.invoke(...)
last = result["messages"][-1]
print(f"Tool calls: {last.tool_calls}")
```

---

## 📦 Dependências

```toml
langchain = "^0.1"
langchain_community = "^0.1"
langchain_openai = "^0.1"
langgraph = "^0.1"
fastapi = "^0.1"
uvicorn = "^0.1"
pyodbc = "^4.x"
python-dateutil = "^2.x"
ipython = "^8.x"
requests = "^2.x"
```

---

## 📝 Licença

Projeto pessoal - Todos os direitos reservados

---

## 👤 Autor

**Rondi** - Projeto 4 - SQL Agent  
Data: Janeiro 2025

---

## 🔗 Recursos Úteis

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [SQL Server ODBC Driver](https://docs.microsoft.com/sql/connect/odbc/)

---

**Última atualização**: 10 de Janeiro de 2025
