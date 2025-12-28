from pydantic import BaseModel, Field
from datetime import datetime
from langgraph.graph.state import RunnableConfig

class RespostaModel(BaseModel):
    """Modelo para respostas de chat"""
    response: str
    data_hora: datetime = Field(default_factory=datetime.utcnow)
    config: RunnableConfig | None = None
    tokens_used: int | None = None
    