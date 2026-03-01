"""Модуль с фабрикой для создания LLM клиентов (обновление)."""

from enum import Enum
from typing import Type, Dict, Any
from logging import getLogger

from .base import BaseLLMClient
from .deepseek_client import DeepSeekLLMClient
from .openai_client import OpenAILLMClient
from .openai_vision_client import OpenAIVisionLLMClient

logger = getLogger(__name__)


class LLMProvider(str, Enum):
    """Поддерживаемые провайдеры LLM."""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    OPENAI_VISION = "openai-vision"  # Новый провайдер для Vision
    # Можно добавить других провайдеров (Claude, Gemini и т.д.)


class LLMClientFactory:
    """
    Фабрика для создания клиентов различных LLM провайдеров.
    Позволяет легко подменять одну модель на другую.
    """
    
    _clients: Dict[LLMProvider, Type[BaseLLMClient]] = {
        LLMProvider.DEEPSEEK: DeepSeekLLMClient,
        LLMProvider.OPENAI: OpenAILLMClient,
        LLMProvider.OPENAI_VISION: OpenAIVisionLLMClient,  # Новый клиент
    }
    
    @classmethod
    def register_client(cls, provider: LLMProvider, client_class: Type[BaseLLMClient]):
        """
        Регистрирует нового провайдера.
        
        Args:
            provider: Провайдер
            client_class: Класс клиента
        """
        cls._clients[provider] = client_class
        logger.info("Зарегистрирован провайдер: %s", provider.value)
    
    @classmethod
    def create_client(cls, provider: LLMProvider, **kwargs) -> BaseLLMClient:
        """
        Создает клиента для указанного провайдера.
        
        Args:
            provider: Провайдер LLM
            **kwargs: Параметры для клиента
        
        Returns:
            Экземпляр клиента
        
        Raises:
            ValueError: Если провайдер не поддерживается
        """
        if provider not in cls._clients:
            supported = ", ".join([p.value for p in cls._clients.keys()])
            raise ValueError(
                f"Провайдер {provider} не поддерживается. "
                f"Поддерживаемые: {supported}"
            )
        
        client_class = cls._clients[provider]
        logger.info("Создан клиент для провайдера: %s", provider.value)
        return client_class(**kwargs)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Возвращает список доступных провайдеров."""
        return [p.value for p in cls._clients.keys()]