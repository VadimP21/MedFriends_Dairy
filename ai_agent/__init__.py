"""
Пакет для работы с LLM моделями через абстрактный интерфейс.
Поддерживает DeepSeek, OpenAI и других провайдеров.
"""

from .base import BaseLLMClient
from .deepseek_client import DeepSeekLLMClient
from .openai_client import OpenAILLMClient
from .factory import LLMClientFactory, LLMProvider
from .client import llm_client, LLMClient
from .service import LLMService, llm_service
from .config import llm_settings
from .food_analysis_service import food_analysis_service, FoodAnalysisService

__all__ = [
    # Базовые классы
    "BaseLLMClient",
    # Конкретные клиенты
    "DeepSeekLLMClient",
    "OpenAILLMClient",
    # Фабрика
    "LLMClientFactory",
    "LLMProvider",
    # Синглтон-клиент
    "llm_client",
    "LLMClient",
    # Сервис
    "llm_service",
    "LLMService",
    # Настройки
    "llm_settings",
    "food_analysis_service",
    "FoodAnalysisService",
]
