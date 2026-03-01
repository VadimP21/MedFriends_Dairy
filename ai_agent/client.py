"""
Модуль содержит синглтон-клиенты для работы с LLM через абстрактную фабрику.
"""

from logging import getLogger
from typing import Any, List, Union

from langchain_core.messages import BaseMessage

from .meta_base import MetaBaseSingleton
from .factory import LLMClientFactory, LLMProvider

logger = getLogger()


class LLMClient(metaclass=MetaBaseSingleton):
    """
    Синглтон-клиент для работы с LLM.
    Позволяет легко переключаться между провайдерами.
    """
    
    _current_provider: LLMProvider = LLMProvider.DEEPSEEK
    _client_instance = None
    
    @classmethod
    def set_provider(cls, provider: LLMProvider):
        """
        Устанавливает провайдера для всех последующих вызовов.
        
        Args:
            provider: Провайдер LLM
        """
        cls._current_provider = provider
        cls._client_instance = None  # Сбрасываем кэш
        logger.info("Установлен провайдер LLM: %s", provider.value)
    
    @classmethod
    def _get_client(cls) -> Any:
        """
        Возвращает или создает экземпляр клиента для текущего провайдера.
        """
        if cls._client_instance is None:
            cls._client_instance = LLMClientFactory.create_client(
                cls._current_provider
            )
        return cls._client_instance
    
    @classmethod
    async def ainvoke(cls, messages: list[BaseMessage], **kwargs) -> str:
        """
        Асинхронный вызов текущей модели.
        
        Args:
            messages: Список сообщений
            **kwargs: Параметры вызова
        
        Returns:
            Ответ модели
        """
        client = cls._get_client()
        return await client.ainvoke(messages, **kwargs)
    
    @classmethod
    async def ainvoke_with_images(
        cls, 
        prompt: str, 
        images: List[Union[str, bytes]], 
        **kwargs
    ) -> str:
        """
        Асинхронный вызов с изображениями (для мультимодальных моделей).
        
        Args:
            prompt: Текстовый промпт
            images: Список изображений
            **kwargs: Параметры вызова
        
        Returns:
            Ответ модели
        """
        client = cls._get_client()
        return await client.ainvoke_with_images(prompt, images, **kwargs)
    
    @classmethod
    def invoke(cls, messages: list[BaseMessage], **kwargs) -> str:
        """
        Синхронный вызов текущей модели.
        """
        client = cls._get_client()
        return client.invoke(messages, **kwargs)
    
    @classmethod
    async def chat(cls, prompt: str, **kwargs) -> str:
        """
        Упрощенный метод для отправки одного промпта.
        
        Args:
            prompt: Текст запроса
            **kwargs: Параметры модели
        
        Returns:
            Ответ модели
        """
        from langchain_core.messages import HumanMessage
        
        messages = [HumanMessage(content=prompt)]
        return await cls.ainvoke(messages, **kwargs)


# Создаем глобальный экземпляр (синглтон)
llm_client = LLMClient()