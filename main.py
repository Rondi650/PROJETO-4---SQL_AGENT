from fastapi import FastAPI
from my_agent import agent
from my_agent.models.request import PerguntaModel
from my_agent.models.response import RespostaModel
import json

app = FastAPI()

@app.post("/chat")
def chat_endpoint(data: PerguntaModel) -> RespostaModel:
    """Endpoint para chat com o agente"""
    pergunta = data.pergunta
    history = []

    for step in agent.stream(
        {"messages": [{"role": "user", "content": pergunta}]},
        config={"configurable": {"thread_id": "api_conversation"}},
        stream_mode="values"
    ):
        msg = step["messages"][-1].content
        msg_completa = step["messages"][-1]
        msg_completa.pretty_print()
             
    # guarde todas as mensagens do step
        history.extend(step["messages"])
    # serialize tudo
    history_serialized = [m.model_dump() for m in history]

    with open("chat_completo.json", "w", encoding="utf-8") as f:
        json.dump(history_serialized, f, ensure_ascii=False, indent=4)
    
    return RespostaModel(
        response=msg,
        thread_id="api_conversation"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Iniciar o servidor com: uvicorn main:app --reload