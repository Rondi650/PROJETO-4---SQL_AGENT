from fastapi import FastAPI
from my_agent import agent
from pydantic import BaseModel, Field
from typing import Annotated

class PerguntaModel(BaseModel):
    pergunta: Annotated[str, Field(min_length=1, max_length=200)]

app = FastAPI()

@app.post("/chat")
def chat_endpoint(data: PerguntaModel):
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
    return {"response": msg}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
