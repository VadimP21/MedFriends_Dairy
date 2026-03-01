"""Модуль с реализацией мультимодального клиента OpenAI Vision."""

from typing import Optional, List, Union, Dict, Any
from logging import getLogger
import base64

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from .base import BaseLLMClient
from .config import llm_settings

logger = getLogger(__name__)


class OpenAIVisionLLMClient(BaseLLMClient):
    """
    Мультимодальный клиент для OpenAI Vision API.
    Поддерживает анализ изображений с едой.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Инициализация клиента OpenAI Vision.
        
        Args:
            api_key: API ключ OpenAI
            **kwargs: Дополнительные параметры
        """
        super().__init__(**kwargs)
        self.api_key = api_key or llm_settings.OPENAI_API_KEY
        self.base_url = kwargs.get("base_url", llm_settings.OPENAI_URL)
        
        if not self.api_key:
            raise ValueError("API ключ OpenAI не предоставлен")
    
    def get_chat_model(self, **kwargs) -> BaseChatModel:
        """
        Возвращает чат-модель OpenAI Vision.
        """
        # Для Vision используем специальную модель
        model = kwargs.get("model", "gpt-4-vision-preview")
        
        model_kwargs = {
            "model": model,
            "temperature": kwargs.get("temperature", 0.3),  # Низкая температура для точности
            "timeout": kwargs.get("timeout", llm_settings.OPENAI_TIMEOUT),
            "max_retries": kwargs.get("max_retries", llm_settings.DEFAULT_MAX_RETRIES),
            "api_key": self.api_key,
            "base_url": self.base_url,
            "max_tokens": kwargs.get("max_tokens", 1000),
            **self._model_kwargs,
            **kwargs
        }
        
        return ChatOpenAI(**model_kwargs)
    
    async def ainvoke(self, messages: list[BaseMessage], **kwargs) -> str:
        """
        Асинхронный вызов OpenAI Vision (текстовый режим).
        """
        chat_model = self.get_chat_model(**kwargs)
        response = await chat_model.ainvoke(messages)
        
        logger.debug("OpenAI Vision response received")
        return response.content
    
    async def ainvoke_with_images(
        self, 
        prompt: str, 
        images: List[Union[str, bytes]], 
        **kwargs
    ) -> str:
        """
        Асинхронный вызов OpenAI Vision с изображениями.
        
        Args:
            prompt: Текстовый промпт (например, "Что это за еда? Рассчитай КБЖУ")
            images: Список изображений (URL или байты)
            **kwargs: Дополнительные параметры
        
        Returns:
            Ответ модели
        """
        # Подготавливаем содержимое сообщения
        content = []
        
        # Добавляем текстовый промпт
        content.append({"type": "text", "text": prompt})
        
        # Добавляем изображения
        for img in images:
            if isinstance(img, str) and img.startswith(("http://", "https://")):
                # URL изображения
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img}
                })
            else:
                # Байты изображения - кодируем в base64
                if isinstance(img, bytes):
                    base64_img = base64.b64encode(img).decode("utf-8")
                else:
                    # Предполагаем, что это уже base64 строка
                    base64_img = img
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_img}"
                    }
                })
        
        # Создаем сообщение
        message = HumanMessage(content=content)
        
        # Получаем модель с поддержкой vision
        model = self.get_chat_model(**kwargs)
        
        # Отправляем запрос
        response = await model.ainvoke([message])
        
        logger.info("Обработано изображений: %d", len(images))
        return response.content