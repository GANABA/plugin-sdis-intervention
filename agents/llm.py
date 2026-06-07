"""Helper get_llm() — même pattern que _lib/llm.py du cours Guyeux."""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm(temperature: float = 0) -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=temperature,
        api_key=os.environ["OPENAI_API_KEY"],
    )
