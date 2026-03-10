"""
Модуль с сервисом для анализа фотографий еды и расчета КБЖУ.
"""

import base64
import logging
import json
import re
from typing import Optional, Any, List, Union

from langchain_core.messages import HumanMessage

from apps.food_diary.schemas import DishCreateIn
from . import LLMClient
from .prompts import food_analise_system_prompt

logger = logging.getLogger(__name__)


class FoodAnalysisService:
    """
    Сервис для анализа фотографий еды и расчета КБЖУ.
        prompt: Системный промпт
    Attributes:
        _client: LLM клиент, назначается через config
    """

    prompt = food_analise_system_prompt

    def __init__(self):
        self._client = LLMClient.create_client()

        logger.info(
            "Инициализирован FoodAnalysisService с клиентом: %s",
            self._client.__class__.__name__,
        )

    def _content_for_openai_deepseek(
        self, images: List[Union[str, bytes]]
    ) -> list[dict[str, str]]:
        """
        Подготовка контента для OpenAI Vision с изображениями.

        Args:
            images: Список изображений (URL или байты)

        Returns:
            content для OpenAI Vision
        """
        content = [{"type": "text", "text": self.prompt}]

        for img in images:
            if isinstance(img, str) and img.startswith(("http://", "https://")):
                # URL изображения
                content.append({"type": "image_url", "image_url": {"url": img}})
            else:
                # Байты изображения - кодируем в base64
                if isinstance(img, bytes):
                    base64_img = base64.b64encode(img).decode("utf-8")
                else:
                    # Предполагаем, что это уже base64 строка
                    base64_img = img

                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"},
                    }
                )
        return content

    async def ainvoke_with_images(
        self,
        images: List[Union[str, bytes]],
    ) -> str:
        """
        Асинхронный вызов OpenAI Vision с изображениями.

        Args:
            images: Список изображений (URL или байты)

        Returns:
            Ответ модели
        """
        # Подготавливаем содержимое сообщения

        # Создаем сообщение
        content = self._content_for_openai_deepseek(images)
        message = HumanMessage(content=content)

        # Получаем модель с поддержкой vision

        # Отправляем запрос
        response = await self._client.ainvoke([message])

        logger.info("Обработано изображений: %d", len(content) - 1)
        return response.content

    async def analyze_food_image(self, image: Union[str, bytes]) -> List[DishCreateIn]:
        """
        Анализирует одно изображение еды.

        Args:
            image: URL изображения или байты
            additional_context: Дополнительный контекст (например, "это обед", "порция большая")

        Returns:
            List[DishCreateIn] с данными о КБЖУ
        """

        try:

            response = await self.ainvoke_with_images(
                images=[image],
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

    @staticmethod
    def _extract_json_from_response(response: str) -> List[dict[str, Any]]:
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
