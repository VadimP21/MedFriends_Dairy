"""Модуль с абстрактным базовым классом для LLM клиентов (расширение)."""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
from logging import getLogger

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.embeddings import Embeddings

logger = getLogger(__name__)


class BaseLLMClient(ABC):
    """
    Абстрактный базовый класс для клиентов LLM.
    Определяет интерфейс, который должны реализовать все конкретные клиенты.
    """

    def __init__(self, **kwargs):
        self._model_kwargs = kwargs

    @abstractmethod
    def get_chat_model(self, **kwargs) -> BaseChatModel:
        """
        Возвращает настроенную чат-модель.

        Args:
            **kwargs: Параметры модели (temperature, max_tokens и т.д.)

        Returns:
            Экземпляр чат-модели LangChain
        """
        pass

    @abstractmethod
    async def ainvoke(self, messages: list[BaseMessage], **kwargs) -> str:
        """
        Асинхронный вызов модели.

        Args:
            messages: Список сообщений
            **kwargs: Дополнительные параметры вызова

        Returns:
            Текст ответа
        """
        pass

    def invoke(self, messages: list[BaseMessage], **kwargs) -> str:
        """
        Синхронный вызов модели.

        Args:
            messages: Список сообщений
            **kwargs: Дополнительные параметры вызова

        Returns:
            Текст ответа
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.ainvoke(messages, **kwargs))

    def get_embeddings(self, **kwargs) -> Optional[Embeddings]:
        """
        Возвращает модель для эмбеддингов, если поддерживается.

        Returns:
            Модель эмбеддингов или None
        """
        return None

    async def ainvoke_with_images(
        self, prompt: str, images: List[Union[str, bytes]], **kwargs
    ) -> str:
        """
        Асинхронный вызов модели с изображениями.
        Базовая реализация выбрасывает исключение - должна быть переопределена
        в мультимодальных клиентах.

        Args:
            prompt: Текстовый промпт
            images: Список изображений (URL или байты)
            **kwargs: Дополнительные параметры

        Returns:
            Текст ответа

        Raises:
            NotImplementedError: Если модель не поддерживает изображения
        """
        raise NotImplementedError(
            f"Клиент {self.__class__.__name__} не поддерживает обработку изображений"
        )
