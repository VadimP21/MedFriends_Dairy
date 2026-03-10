"""
Пакет для работы с LLM моделями через абстрактный интерфейс.
Поддерживает DeepSeek, OpenAI и других провайдеров.
"""

from .client import llm_client, LLMClient
from .config import llm_settings
from .food_analysis_service import food_analysis_service, FoodAnalysisService

__all__ = [
    # Синглтон-клиент
    "llm_client",
    "LLMClient",
    # Настройки
    "llm_settings",
    # Сервис
    "food_analysis_service",
    "FoodAnalysisService",
]
