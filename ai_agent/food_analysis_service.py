"""
Модуль с сервисом для анализа фотографий еды и расчета КБЖУ.
"""

import logging
import json
import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from apps.food_diary.schemas import DishCreateIn
from .base import BaseLLMClient
from .openai_vision_client import OpenAIVisionLLMClient

logger = logging.getLogger(__name__)


class FoodAnalysisService:
    """
    Сервис для анализа фотографий еды и расчета КБЖУ.
    Использует мультимодальный LLM клиент.
    """

    FOOD_ANALYSIS_SYSTEM_PROMPT = """
Ты - эксперт по питанию и диетологии с 15-летним опытом. 
Твоя задача - анализировать фотографии еды или аудио сообщения с описанием еды и определять её пищевую ценность.

ТВОИ ОГРАНИЧЕНИЯ И ПРАВИЛА:
1. Отвечай только в формате JSON без каких-либо дополнительных текстов
2. Не включай markdown разметку в ответ
3. Если не уверен в продукте - укажи это в score
4. Всегда оценивай размер порции относительно стандартных размеров
5. Используй средние значения пищевой ценности для продуктов
6. Для составных блюд разбивай на основные компоненты
7. Всегда указывай вес в граммах, калории в ккал, а также белки, жиры и углеводы с точностью до одного знака после запятой
8. Если видишь несколько продуктов - анализируй каждый отдельно
9. Учитывай способ приготовления (жареное, вареное, сырое и т.д.)
10. Для напитков указывай объем в мл

ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:
- Пользователь находится в России, используй распространенные там продукты
- Учитывай сезонность продуктов
- Стандартный размер тарелки: 25см диаметр
- Стандартный стакан: 250мл

Верни результат строго в формате JSON со следующей структурой:

[
        {
          "name": "название блюда",
          "weight": float (г),
          "calories": integer (ккал),
          "protein": float (г),
          "fat": float (г),
          "carbohydrates": float (г),
        },
        {
          "name": "название блюда 2",
          "weight": float (г),
          "calories": integer (ккал),
          "protein": float (г),
          "fat": float (г),
          "carbohydrates": float (г),
        }
]
        
Не добавляй никакого текста кроме JSON.
"""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        """
        Инициализация сервиса анализа еды.

        Args:
            llm_client: Мультимодальный LLM клиент.
                       Если не указан, создается OpenAIVisionLLMClient.
        """
        self._client = llm_client or OpenAIVisionLLMClient()

        logger.info(
            "Инициализирован FoodAnalysisService с клиентом: %s",
            self._client.__class__.__name__,
        )

    async def analyze_food_image(
        self, image: Union[str, bytes], additional_context: Optional[str] = None
    ) -> List[DishCreateIn]:
        """
        Анализирует одно изображение еды.

        Args:
            image: URL изображения или байты
            additional_context: Дополнительный контекст (например, "это обед", "порция большая")

        Returns:
            List[DishCreateIn] с данными о КБЖУ
        """
        prompt = self._build_analysis_prompt(additional_context)

        try:
            response = await self._client.ainvoke_with_images(
                prompt=prompt,
                images=[image],
                temperature=0.2,  # Низкая температура для точности
                max_tokens=1000,
            )

            # Извлекаем JSON из ответа
            dishes_data = self._extract_json_from_response(response)

            # Создаем список DishCreateIn из полученных данных
            return [
                DishCreateIn(
                    name=dish_data.get("name", "Неизвестное блюдо"),
                    weight=float(dish_data.get("weight", 0)),
                    calories=int(dish_data.get("calories", 0)),
                    protein=float(dish_data.get("protein", 0)),
                    fat=float(dish_data.get("fat", 0)),
                    carbohydrates=float(dish_data.get("carbohydrates", 0)),
                )
                for dish_data in dishes_data
            ]

        except Exception as e:
            logger.error("Ошибка при анализе изображения: %s", str(e))
            raise

    async def analyze_multiple_food_images(
        self, images: List[Union[str, bytes]], additional_context: Optional[str] = None
    ) -> List[DishCreateIn]:
        """
        Анализирует несколько изображений еды (например, несколько блюд).

        Args:
            images: Список изображений
            additional_context: Дополнительный контекст

        Returns:
            Список списков DishCreateIn для каждого изображения
        """
        results = []

        for i, image in enumerate(images):
            logger.info("Анализ изображения %d из %d", i + 1, len(images))
            try:
                result = await self.analyze_food_image(image, additional_context)
                results.extend(result)
            except Exception as e:
                logger.error("Ошибка при анализе изображения %d: %s", i + 1, str(e))
                # Добавляем "пустой" результат с низкой уверенностью
                results.extend(
                    [
                        DishCreateIn(
                            name=f"Ошибка анализа {i + 1}",
                            weight=0,
                            calories=0,
                            protein=0,
                            fat=0,
                            carbohydrates=0,
                        )
                    ]
                )

        return results

    def _build_analysis_prompt(self, additional_context: Optional[str] = None) -> str:
        """Формирует промпт для анализа."""
        prompt = self.FOOD_ANALYSIS_SYSTEM_PROMPT

        if additional_context:
            prompt += (
                f"\n\nДополнительная информация от пользователя: {additional_context}"
            )

        prompt += "\n\nАнализируй изображение и верни JSON с данными о блюде."

        return prompt

    def _extract_json_from_response(self, response: str) -> List[dict[str, Any]]:
        """
        Извлекает JSON из ответа модели.

        Args:
            response: Ответ модели

        Returns:
            Список словарей с данными
        """
        # Ищем JSON массив в ответе
        json_match = re.search(r"\[.*\]", response, re.DOTALL)

        if json_match:
            json_str = json_match.group()
        else:
            # Если нет массива, ищем объект
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = f"[{json_match.group()}]"
            else:
                json_str = response

        # Пробуем распарсить
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Не удалось распарсить JSON, возвращаем пустой список")
            return [
                {
                    "name": "Не удалось распознать",
                    "weight": 0,
                    "calories": 0,
                    "protein": 0,
                    "fat": 0,
                    "carbohydrates": 0,
                }
            ]


food_analysis_service = FoodAnalysisService()
