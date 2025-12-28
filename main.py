from fastapi import FastAPI
from my_agent import agent
from my_agent.models.request import PerguntaModel
from my_agent.models.response import RespostaModel
from langchain_core.messages import HumanMessage
from my_agent.config.settings import runnable_config
from rich import print
from rich.markdown import Markdown

app = FastAPI()

@app.post("/chat")
def chat_endpoint(data: PerguntaModel) -> RespostaModel:
    """Endpoint para chat com o agente"""
    pergunta = data.pergunta

    for step in agent.stream(
        {"messages": [HumanMessage(content=pergunta)]},
        config=runnable_config(),
        stream_mode="values"
    ):
        print(step)
        print(Markdown("---"))
        
        msg = step["messages"][-1].content
 
    return RespostaModel(
        response=msg, 
        config=runnable_config()
    )
    
# Iniciar o servidor com: uvicorn main:app --reload