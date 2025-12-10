from fastapi import FastAPI
from my_agent import agent
from my_agent.models.request import PerguntaModel
from my_agent.models.response import RespostaModel

app = FastAPI()

@app.post("/chat")
def chat_endpoint(data: PerguntaModel) -> RespostaModel:
    """Endpoint para chat com o agente"""
    pergunta = data.pergunta
    for step in agent.stream(
        {"messages": [{"role": "user", "content": pergunta}]},
        config={"configurable": {"thread_id": "api_conversation"}},
        stream_mode="values"
    ):
        msg = step["messages"][-1].content
        msg_completa = step["messages"][-1]
        msg_completa.pretty_print()
        
    return RespostaModel(
        response=msg,
        thread_id="api_conversation"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Iniciar o servidor com: uvicorn main:app --reload