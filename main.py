from fastapi import FastAPI
from my_agent import agent
from my_agent.models.request import PerguntaModel
from my_agent.models.response import RespostaModel
from langchain_core.messages import HumanMessage, AIMessage
from my_agent.config.settings import runnable_config
from rich import print
from rich.markdown import Markdown

app = FastAPI()

@app.post("/chat")
def chat_endpoint(data: PerguntaModel) -> RespostaModel:
    """Endpoint para chat com o agente"""
    pergunta = data.pergunta
    msg = ""

    total_tokens = 0
    for step in agent.stream(
        {"messages": [HumanMessage(content=pergunta)]},
        config=runnable_config(),
        stream_mode="values"
    ):
        print(step)
        print(Markdown("---"))
        
        last_message = step["messages"][-1]
        msg = last_message.content
 
        if isinstance(last_message, AIMessage) and hasattr(last_message, 'usage_metadata'):
            tokens = last_message.usage_metadata.get("total_tokens", 0)
            total_tokens += tokens
            print(Markdown(f"### Tokens nesta etapa: {tokens}"))
            print(Markdown(f"### Tokens usados até agora: {total_tokens}"))
            
    return RespostaModel(
        response=msg, 
        config=runnable_config(),
        tokens_used=total_tokens
    )
    
# Iniciar o servidor com: uvicorn main:app --reload