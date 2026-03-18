from __future__ import annotations

from langchain.chat_models import BaseChatModel, init_chat_model
from langchain_openai import OpenAIEmbeddings

LLM_MODEL: str = "gpt-4.1-mini"
EMBEDDING_MODEL: str = "text-embedding-3-small"


def create_llm() -> BaseChatModel:
    return init_chat_model(model=LLM_MODEL)


def create_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)
