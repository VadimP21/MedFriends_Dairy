"""
Модуль содержит клиент для работы с LLM.
"""

from dataclasses import dataclass
from logging import getLogger

from gigachat import GigaChat
from langchain_openai import ChatOpenAI

from ai_agent.config import LLMProvider, llm_settings

logger = getLogger()


@dataclass(frozen=True)
class LLMClient:
    """
    Клиент для работы с LLM.
    Переключение между провайдерами осуществляется через llm_settings.
    """

    _current_provider: LLMProvider = llm_settings.active_provider
    settings = llm_settings

    @classmethod
    def create_client(cls) -> ChatOpenAI | GigaChat:
        """
        Возвращает экземпляр клиента для текущего провайдера.
        """

        if not cls._current_provider:
            raise ValueError(f"Unsupported provider: {cls._current_provider}")

        provider_config = cls.settings.get_provider_config(cls._current_provider)
        common_settings = cls.settings.get_common_config()
        total_provider_settings = {**provider_config, **common_settings}

        logger.info("total_provider_settings: %s", total_provider_settings)

        clients = {
            "gigachat": GigaChat(**total_provider_settings),
            # "openai": ChatOpenAI(**total_provider_settings),
            # "deepseek": ChatOpenAI(**total_provider_settings),
        }
        return clients[cls._current_provider]


llm_client = LLMClient()
