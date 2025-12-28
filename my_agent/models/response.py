from pydantic import BaseModel, Field
from datetime import datetime

class RespostaModel(BaseModel):
    """Modelo para respostas de chat"""
    response: str
    data_hora: datetime = Field(default_factory=datetime.utcnow)