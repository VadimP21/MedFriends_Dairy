"""Модуль с реализацией клиента OpenAI."""

from typing import Optional
from logging import getLogger

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .base import BaseLLMClient
from .config import llm_settings

logger = getLogger(__name__)


class OpenAILLMClient(BaseLLMClient):
    """
    Конкретная реализация клиента для OpenAI.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Инициализация клиента OpenAI.
        """
        super().__init__(**kwargs)
        self.api_key = api_key or llm_settings.OPENAI_API_KEY
        self.base_url = kwargs.get("base_url", llm_settings.OPENAI_URL)

        if not self.api_key:
            raise ValueError("API ключ OpenAI не предоставлен")

    def get_chat_model(self, **kwargs) -> BaseChatModel:
        """
        Возвращает чат-модель OpenAI.
        """
        model_kwargs = {
            "model": kwargs.get("model", llm_settings.OPENAI_MODEL),
            "temperature": kwargs.get("temperature", llm_settings.DEFAULT_TEMPERATURE),
            "timeout": kwargs.get("timeout", llm_settings.OPENAI_TIMEOUT),
            "max_retries": kwargs.get("max_retries", llm_settings.DEFAULT_MAX_RETRIES),
            "api_key": self.api_key,
            "base_url": self.base_url,
            **self._model_kwargs,
            **kwargs,
        }

        return ChatOpenAI(**model_kwargs)

    async def ainvoke(self, messages: list[BaseMessage], **kwargs) -> str:
        """
        Асинхронный вызов OpenAI.
        """
        chat_model = self.get_chat_model(**kwargs)
        response = await chat_model.ainvoke(messages)

        logger.debug("OpenAI response received")
        return response.content

    def get_embeddings(self, **kwargs) -> Optional[Embeddings]:
        """
        Возвращает модель эмбеддингов OpenAI.
        """
        return OpenAIEmbeddings(
            api_key=self.api_key, model=kwargs.get("model", "text-embedding-ada-002")
        )
