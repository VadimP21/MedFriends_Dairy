"""
Модуль содержит синглтон-клиенты для работы с LLM через абстрактную фабрику.
"""

from logging import getLogger
from typing import Any, List, Union

from gigachat import GigaChat
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from ai_agent.config import LLMProvider, llm_settings

logger = getLogger()


class LLMClient:
    """
    Синглтон-клиент для работы с LLM.
    Переключение между провайдерами осуществляется через llm_settings.
    """

    _current_provider: LLMProvider = llm_settings.active_provider
    settings = llm_settings

    @classmethod
    def create_client(cls, provider = _current_provider) -> ChatOpenAI:
        """
        Возвращает экземпляр клиента для текущего провайдера.
        """
        # if cls._client_instance is None:
        #     cls._client_instance = LLMClientFactory.create_client(cls._current_provider)
        # return cls._client_instance

        if not provider:
            raise ValueError(f"Unsupported provider: {cls.provider}")

        provider_config = cls.settings.get_provider_config(provider)
        common_settings = cls.settings.get_common_config()
        total_provider_settings = {**provider_config, **common_settings}

        logger.info("total_provider_settings: %s", total_provider_settings)

        clients = {
            "gigachat": GigaChat(**total_provider_settings),
            "openai": ChatOpenAI(**total_provider_settings),
            "deepseek": ChatOpenAI(**total_provider_settings),

        }
        x = ChatOpenAI(**total_provider_settings)
        return x



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
        cls, prompt: str, images: List[Union[str, bytes]], **kwargs
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
