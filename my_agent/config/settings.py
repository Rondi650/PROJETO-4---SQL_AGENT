import os

from dotenv import load_dotenv
from langgraph.graph.state import RunnableConfig
from typing import Literal
from langchain.chat_models import BaseChatModel, init_chat_model

load_dotenv()

LLM_MODEL = "gpt-5.1-2025-11-13"
MODEL_PROVIDER = "openai"
LLM_TEMPERATURE = 0

def runnable_config() -> RunnableConfig:
    user_type: Literal["plus", "enterprise"] = "plus"
    configurable={
        "thread_id": "default_thread",
        "User_type": user_type,
        "temperature": LLM_TEMPERATURE,
        }
    return RunnableConfig(configurable=configurable)


def load_llm() -> BaseChatModel:
    llm = init_chat_model(
        api_key=os.getenv("OPENAI_API_KEY"), 
        model=LLM_MODEL, 
        model_provider="openai",
        temperature=LLM_TEMPERATURE
    )
    
    return llm