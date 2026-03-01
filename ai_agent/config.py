"""Модуль содержит конфигурационные настройки для работы с LLM."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Настройки для LLM провайдеров."""
    
    # DeepSeek
    DEEPSEEK_API_KEY: str = "1"
    DEEPSEEK_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_TIMEOUT: int = 120
    
    # OpenAI (пример другого провайдера)
    OPENAI_API_KEY: str = "1"
    OPENAI_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TIMEOUT: int = 60
    
    # Общие настройки
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_RETRY_DELAY: float = 1.0
    DEFAULT_TEMPERATURE: float = 0.7
    
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        env_prefix="LLM_"
    )


llm_settings = LLMSettings()