"""Модуль с реализацией клиента DeepSeek."""

from typing import Optional, Any
from logging import getLogger

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI

from .base import BaseLLMClient
from .config import llm_settings

logger = getLogger(__name__)


class DeepSeekLLMClient(BaseLLMClient):
    """
    Конкретная реализация клиента для DeepSeek API.
    DeepSeek совместим с OpenAI API, поэтому используем ChatOpenAI из langchain-openai.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Инициализация клиента DeepSeek.
        
        Args:
            api_key: API ключ DeepSeek (если None, берется из настроек)
            **kwargs: Дополнительные параметры
        """
        super().__init__(**kwargs)
        self.api_key = api_key or llm_settings.DEEPSEEK_API_KEY
        self.base_url = kwargs.get("base_url", llm_settings.DEEPSEEK_URL)
        
        if not self.api_key:
            raise ValueError("API ключ DeepSeek не предоставлен")
    
    def get_chat_model(self, **kwargs) -> BaseChatModel:
        """
        Возвращает чат-модель DeepSeek через OpenAI-совместимый интерфейс.
        """
        # Объединяем параметры
        model_kwargs = {
            "model": kwargs.get("model", llm_settings.DEEPSEEK_MODEL),
            "temperature": kwargs.get("temperature", llm_settings.DEFAULT_TEMPERATURE),
            "timeout": kwargs.get("timeout", llm_settings.DEEPSEEK_TIMEOUT),
            "max_retries": kwargs.get("max_retries", llm_settings.DEFAULT_MAX_RETRIES),
            "api_key": self.api_key,
            "base_url": self.base_url,
            **self._model_kwargs,
            **kwargs
        }
        
        # DeepSeek совместим с OpenAI API
        return ChatOpenAI(**model_kwargs)
    
    async def ainvoke(self, messages: list[BaseMessage], **kwargs) -> str:
        """
        Асинхронный вызов DeepSeek.
        """
        chat_model = self.get_chat_model(**kwargs)
        response = await chat_model.ainvoke(messages)
        
        logger.debug(
            "DeepSeek response received. Input tokens: ~%d",
            len(str(messages)) // 4  # Примерная оценка
        )
        
        return response.content
    
    def get_embeddings(self, **kwargs) -> Optional[Embeddings]:
        """
        DeepSeek пока не поддерживает эмбеддинги через публичное API.
        """
        logger.warning("DeepSeek не поддерживает эмбеддинги")
        return None