from pydantic import BaseModel, Field
from typing import Annotated

class PerguntaModel(BaseModel):
    pergunta: Annotated[str, Field(min_length=1, max_length=200)]
    
class QueryParams(BaseModel):
    """Parâmetros para filtros de queries"""
    agent: str | None = None
    topic: str | None = None
    data_inicio: str = Field(description="Data de início no formato 'YYYY-MM-DD'")
    data_fim: str = Field(description="Data de fim no formato 'YYYY-MM-DD'")