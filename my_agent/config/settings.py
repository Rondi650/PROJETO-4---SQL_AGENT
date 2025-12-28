import os

from dotenv import load_dotenv
from langgraph.graph.state import RunnableConfig
from typing import Literal
from pydantic import SecretStr
from langchain.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

load_dotenv()

LLM_MODEL = "gpt-5.1-2025-11-13"
MODEL_PROVIDER = "openai"
LLM_TEMPERATURE = 0

def runnable_config() -> RunnableConfig:
    user_type: Literal["plus", "enterprise", "basic"] = "plus"
    configurable={
        "thread_id": "default_thread",
        "user_type": user_type,
        "temperature": 1 if user_type == "plus" else 0
        }
    return RunnableConfig(
        run_name='MODELO DO RONDI',
        configurable=configurable,
        max_concurrency=2,
        recursion_limit=5
        )

def load_llm(temperature: float | None = None) -> BaseChatModel:
    temp = LLM_TEMPERATURE if temperature is None else temperature
    llm = ChatOpenAI(
        api_key=SecretStr(os.getenv("OPENAI_API_KEY") or ""),
        model=LLM_MODEL,
        temperature=temp,
    )
    return llm
