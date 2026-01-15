import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langgraph.graph.state import RunnableConfig

load_dotenv()

THREAD_CONFIG = RunnableConfig(configurable={"thread_id": "default_thread"},
                               recursion_limit=5)

LLM_MODEL = "gpt-5.1-2025-11-13"
LLM_TEMPERATURE = 0

api_key = SecretStr(os.getenv("OPENAI_API_KEY") or "")

llm = ChatOpenAI(api_key=api_key, model=LLM_MODEL, temperature=LLM_TEMPERATURE)