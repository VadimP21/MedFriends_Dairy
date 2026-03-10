# """
# Модуль с сервисом, который использует абстрактный LLM клиент.
# Это основной сервис, который выполняет бизнес-логику.
# """
#
# import logging
# from typing import Optional, Any, Dict, List
#
# from langchain_core.messages import HumanMessage, SystemMessage
#
# from .base import BaseLLMClient
# from .factory import LLMClientFactory, LLMProvider
# from .client import LLMClient
#
# logger = logging.getLogger(__name__)
#
#
# class LLMService:
#     """
#     Сервис для работы с LLM.
#     Принимает абстрактный клиент и выполняет бизнес-логику.
#     """
#
#     def __init__(self, llm_client: BaseLLMClient = None):
#         """
#         Инициализация сервиса.
#
#         Args:
#             llm_client: Абстрактный клиент LLM.
#                        Если не указан, используется синглтон.
#         """
#         if llm_client is None:
#             # Получаем клиент из синглтона
#             self._client = LLMClient._get_client()  # ✅ правильно
#         else:
#             self._client = llm_client
#         logger.info(
#             "Инициализирован LLMService с клиентом: %s", self._client.__class__.__name__
#         )
#
#     @classmethod
#     def create_for_provider(cls, provider: LLMProvider, **kwargs):
#         """
#         Создает сервис для конкретного провайдера.
#
#         Args:
#             provider: Провайдер LLM
#             **kwargs: Параметры для клиента
#
#         Returns:
#             Экземпляр сервиса
#         """
#         client = LLMClientFactory.create_client(provider, **kwargs)
#         return cls(client)
#
#     async def generate_response(
#         self,
#         prompt: str,
#         system_prompt: Optional[str] = None,
#         temperature: float = 0.7,
#         max_tokens: Optional[int] = None,
#         **kwargs,
#     ) -> str:
#         """
#         Генерирует ответ на основе промпта.
#
#         Args:
#             prompt: Пользовательский запрос
#             system_prompt: Системный промпт (опционально)
#             temperature: Температура генерации
#             max_tokens: Максимальное количество токенов
#             **kwargs: Дополнительные параметры
#
#         Returns:
#             Сгенерированный ответ
#         """
#         messages = []
#
#         if system_prompt:
#             messages.append(SystemMessage(content=system_prompt))
#
#         messages.append(HumanMessage(content=prompt))
#
#         logger.debug("Отправка запроса в LLM. Длина промпта: %d символов", len(prompt))
#
#         response = await self._client.ainvoke(
#             messages, temperature=temperature, max_tokens=max_tokens, **kwargs
#         )
#
#         logger.debug("Получен ответ. Длина: %d символов", len(response))
#         return response
#
#     async def chat_with_history(self, messages: List[Dict[str, str]], **kwargs) -> str:
#         """
#         Ведет диалог с учетом истории.
#
#         Args:
#             messages: Список сообщений в формате
#                      [{"role": "user", "content": "..."},
#                       {"role": "assistant", "content": "..."}]
#             **kwargs: Параметры генерации
#
#         Returns:
#             Ответ ассистента
#         """
#         from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
#
#         langchain_messages = []
#
#         for msg in messages:
#             if msg["role"] == "system":
#                 langchain_messages.append(SystemMessage(content=msg["content"]))
#             elif msg["role"] == "user":
#                 langchain_messages.append(HumanMessage(content=msg["content"]))
#             elif msg["role"] == "assistant":
#                 langchain_messages.append(AIMessage(content=msg["content"]))
#
#         response = await self._client.ainvoke(langchain_messages, **kwargs)
#         return response
#
#     async def classify_intent(
#         self, query: str, intents: Dict[str, str], **kwargs
#     ) -> str:
#         """
#         Классифицирует намерение пользователя.
#
#         Args:
#             query: Запрос пользователя
#             intents: Словарь {название_интента: описание}
#             **kwargs: Параметры генерации
#
#         Returns:
#             Название интента
#         """
#         # Формируем описание интентов
#         intents_desc = "\n".join(
#             [f"- {name}: {desc}" for name, desc in intents.items()]
#         )
#
#         system_prompt = f"""Ты - классификатор намерений.
# Определи, к какому интенту относится запрос пользователя.
#
# Доступные интенты:
# {intents_desc}
#
# Ответь ТОЛЬКО названием интента, без пояснений."""
#
#         response = await self.generate_response(
#             prompt=query,
#             system_prompt=system_prompt,
#             temperature=0.1,  # Низкая температура для детерминизма
#             max_tokens=50,
#             **kwargs,
#         )
#
#         # Очищаем ответ
#         intent = response.strip().lower()
#
#         # Проверяем, что интент есть в списке
#         if intent not in intents:
#             logger.warning("Получен неизвестный интент: %s", intent)
#             return "unknown"
#
#         return intent
#
#     async def extract_entities(
#         self, query: str, entity_types: List[str], **kwargs
#     ) -> Dict[str, Any]:
#         """
#         Извлекает сущности из запроса.
#
#         Args:
#             query: Запрос пользователя
#             entity_types: Список типов сущностей для извлечения
#             **kwargs: Параметры генерации
#
#         Returns:
#             Словарь с извлеченными сущностями
#         """
#         import json
#
#         entity_types_str = ", ".join(entity_types)
#
#         system_prompt = f"""Ты - система извлечения сущностей.
# Извлеки из запроса пользователя следующие сущности: {entity_types_str}.
#
# Верни результат строго в формате JSON, например:
# {{"entity1": "значение", "entity2": "значение"}}
#
# Если сущность не найдена, верни null для нее."""
#
#         response = await self.generate_response(
#             prompt=query,
#             system_prompt=system_prompt,
#             temperature=0.1,
#             max_tokens=200,
#             **kwargs,
#         )
#
#         # Пытаемся распарсить JSON
#         try:
#             # Ищем JSON в ответе
#             import re
#
#             json_match = re.search(r"\{.*\}", response, re.DOTALL)
#             if json_match:
#                 return json.loads(json_match.group())
#             return json.loads(response)
#         except json.JSONDecodeError:
#             logger.error("Не удалось распарсить JSON из ответа: %s", response)
#             return {}
#
#     async def summarize(
#         self, text: str, max_length: Optional[int] = None, **kwargs
#     ) -> str:
#         """
#         Суммаризирует текст.
#
#         Args:
#             text: Текст для суммаризации
#             max_length: Максимальная длина суммаризации
#             **kwargs: Параметры генерации
#
#         Returns:
#             Краткое содержание
#         """
#         system_prompt = (
#             "Ты - система суммаризации. Кратко изложи основное содержание текста."
#         )
#
#         if max_length:
#             system_prompt += f" Ограничь ответ {max_length} словами."
#
#         return await self.generate_response(
#             prompt=text, system_prompt=system_prompt, temperature=0.5, **kwargs
#         )
#
#
# # Создаем глобальный экземпляр сервиса с синглтон-клиентом
# llm_service = LLMService()
