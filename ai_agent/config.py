"""Модуль содержит конфигурационные настройки для работы с LLM."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, validator, model_validator
from typing import Optional, Dict, Any
from enum import Enum


class LLMProvider(str, Enum):
    """Доступные провайдеры LLM"""
    OPENAI = "openai"
    GIGACHAT = "gigachat"
    GEMINI = "gemini"


class LLMSettings(BaseSettings):
    """
    Расширенные настройки для LLM клиентов.
    """

    # Выбор активного провайдера
    active_provider: LLMProvider = Field(
        LLMProvider.OPENAI,
        description="Активный LLM провайдер",
        validation_alias="ACTIVE_LLM_PROVIDER"
    )

    # OpenAI
    openai_api_key: Optional[SecretStr] = Field(
        None,
        description="OpenAI API ключ",
        validation_alias="OPENAI_API_KEY"
    )
    openai_base_url: str = Field(
        "https://api.openai.com/v1",
        description="OpenAI base URL",
        validation_alias="OPENAI_BASE_URL"
    )
    openai_model: str = Field(
        "gpt-4-vision-preview",
        description="OpenAI модель по умолчанию",
        validation_alias="OPENAI_MODEL"
    )

    # GigaChat
    gigachat_credentials: Optional[SecretStr] = Field(
        None,
        description="GigaChat авторизационные данные (base64 encoded)",
        validation_alias="GIGACHAT_CREDENTIALS"
    )
    gigachat_scope: str = Field(
        "GIGACHAT_API_PERS",
        description="GigaChat scope",
        validation_alias="GIGACHAT_SCOPE"
    )
    gigachat_model: str = Field(
        "GigaChat",
        description="GigaChat модель",
        validation_alias="GIGACHAT_MODEL"
    )
    gigachat_base_url: str = Field(
        "https://gigachat.devices.sberbank.ru/api/v1",
        description="GigaChat API URL",
        validation_alias="GIGACHAT_BASE_URL"
    )

    # Google Gemini
    gemini_api_key: Optional[SecretStr] = Field(
        None,
        description="Google Gemini API ключ",
        validation_alias="GEMINI_API_KEY"
    )
    gemini_model: str = Field(
        "gemini-pro-vision",
        description="Gemini модель",
        validation_alias="GEMINI_MODEL"
    )

    # Общие настройки
    default_timeout: int = Field(
        30,
        description="Таймаут по умолчанию в секундах",
        validation_alias="DEFAULT_TIMEOUT",
        ge=1,
        le=120
    )

    default_max_retries: int = Field(
        3,
        description="Количество повторных попыток по умолчанию",
        validation_alias="DEFAULT_MAX_RETRIES",
        ge=0,
        le=10
    )

    temperature: float = Field(
        0.3,
        description="Температура для генерации",
        validation_alias="LLM_TEMPERATURE",
        ge=0.0,
        le=2.0
    )

    max_tokens: int = Field(
        1000,
        description="Максимальное количество токенов",
        validation_alias="LLM_MAX_TOKENS",
        ge=1,
        le=4096
    )

    # Настройки модели Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_active_provider(self) -> "LLMSettings":
        """Проверяет наличие ключей для активного провайдера"""
        provider = self.active_provider

        if provider == LLMProvider.OPENAI and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when active_provider is OPENAI")

        if provider == LLMProvider.GIGACHAT and not self.gigachat_credentials:
            raise ValueError("GIGACHAT_CREDENTIALS is required when active_provider is GIGACHAT")

        if provider == LLMProvider.GEMINI and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when active_provider is GEMINI")

        return self

    def get_provider_config(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """
        Возвращает конфигурацию для указанного провайдера.
        """
        provider = provider or self.active_provider

        configs = {
            LLMProvider.OPENAI: {
                "api_key": self.openai_api_key.get_secret_value() if self.openai_api_key else None,
                "base_url": self.openai_base_url,
                "model": self.openai_model,
            },
            LLMProvider.GIGACHAT: {
                "credentials": self.gigachat_credentials.get_secret_value() if self.gigachat_credentials else None,
                "scope": self.gigachat_scope,
                "model": self.gigachat_model,
                "base_url": self.gigachat_base_url,
                "verify_ssl_certs": False,
            },
            LLMProvider.GEMINI: {
                "api_key": self.gemini_api_key.get_secret_value() if self.gemini_api_key else None,
                "model": self.gemini_model,
            }
        }

        return configs[provider]

    def get_common_config(self) -> Dict[str, Any]:
        """Возвращает общие настройки"""
        return {
            "timeout": self.default_timeout,
            "max_retries": self.default_max_retries,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


# Создаем глобальный экземпляр
llm_settings = LLMSettings()

# class LLMSettings(BaseSettings):
#     """Настройки для LLM провайдеров."""
#
#     # DeepSeek
#     DEEPSEEK_API_KEY: str = "1"
#     DEEPSEEK_URL: str = "https://api.deepseek.com"
#     DEEPSEEK_MODEL: str = "deepseek-chat"
#     DEEPSEEK_TIMEOUT: int = 120
#
#     # OpenAI (пример другого провайдера)
#     OPENAI_API_KEY: str = "1"
#     OPENAI_URL: str = "https://api.openai.com/v1"
#     OPENAI_MODEL: str = "gpt-3.5-turbo"
#     OPENAI_TIMEOUT: int = 60
#
#     # Общие настройки
#     DEFAULT_MAX_RETRIES: int = 3
#     DEFAULT_RETRY_DELAY: float = 1.0
#     DEFAULT_TEMPERATURE: float = 0.7
#
#     model_config = SettingsConfigDict(
#         extra="ignore", case_sensitive=False, env_prefix="LLM_"
#     )
#
#
# llm_settings = LLMSettings()
