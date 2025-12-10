import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()

LLM_MODEL = "gpt-5.1-2025-11-13"
LLM_TEMPERATURE = 0

api_key = SecretStr(os.getenv("OPENAI_API_KEY") or "")

llm = ChatOpenAI(api_key=api_key, model=LLM_MODEL, temperature=LLM_TEMPERATURE)