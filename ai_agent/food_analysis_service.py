"""
Модуль с сервисом для анализа фотографий еды и расчета КБЖУ.
"""

import base64
import logging
import json
import re
from pprint import pprint
from typing import Any, List, Union

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from gigachat import GigaChat, Messages, Chat

from apps.food_diary.schemas import DishCreateIn
from . import LLMClient
from .prompts import food_analise_system_prompt, food_analise_system_prompt_mini

logger = logging.getLogger(__name__)


class FoodAnalysisService:
    """
    Сервис для анализа фотографий еды и расчета КБЖУ через LLM.
    """

    prompt = food_analise_system_prompt_mini

    def __init__(self, llm_client=None):
        """Инициализирует сервис с LLM клиентом."""
        if llm_client is None:
            self._client = LLMClient.create_client()
        else:
            self._client = llm_client
        logger.info(
            "Инициализирован FoodAnalysisService с клиентом: %s",
            self._client.__class__.__name__,
        )

    async def analyze_food_image(self, images_bytes: List[bytes]) -> List[DishCreateIn]:
        """
        Анализирует изображение еды и возвращает список блюд с КБЖУ.

        Args:
            images_bytes: Список изображений в виде байтов
        Returns:
            List[DishCreateIn] с данными о КБЖУ
        """
        try:
            response = await self._ainvoke(images_bytes=images_bytes)
            print("FoodAnalysisService.analyze_food_image")
            pprint(response)
            dishes_data = self._extract_json_from_response(response)

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

    async def _ainvoke(
        self,
        images_bytes: List[bytes],
    ) -> str | list[Any]:
        """
        Отправляет изображения в LLM и возвращает сырой ответ.

        Args:
            images_bytes: Список изображений в виде байтов
        Returns:
            Ответ модели
        """
        try:
            if isinstance(self._client, ChatOpenAI):
                content = self._content_for_openai_deepseek(images_bytes)
                message = HumanMessage(content=content)
                response = await self._client.ainvoke([message])
                result = response.content

            if isinstance(self._client, GigaChat):
                self._client.get_token()

                uploaded_files_ids = self._upload_photo_to_gigachat(
                    images_bytes=images_bytes
                )

                payload = self._payload_for_gigachat(uploaded_files_ids)

                response = self._client.chat(payload=payload)
                print("_ainvoke._client.chat", response)

                response = self._client.chat(payload)

                result = [ch.message.content for ch in response.choices]
                print("_ainvoke.result", result)
            else:
                raise Exception(f"No active LLM Provider")

            logger.info("Обработано изображений: %d", len(images_bytes))

        except Exception as e:
            raise

        return result

    def _content_for_openai_deepseek(
        self, images: List[Union[str, bytes]]
    ) -> list[dict[str, str]]:
        """
        Формирует контент для OpenAI Vision с изображениями.

        Args:
            images: Список изображений (URL или байты)

        Returns:
            Контент для отправки в OpenAI
        """
        content = [{"type": "text", "text": self.prompt}]

        for img in images:
            if isinstance(img, str) and img.startswith(("http://", "https://")):
                content.append({"type": "image_url", "image_url": {"url": img}})
            else:
                if isinstance(img, bytes):
                    base64_img = base64.b64encode(img).decode("utf-8")
                else:
                    base64_img = img

                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"},
                    }
                )
        return content

    def _payload_for_gigachat(
        self, images_ids: List[str]
    ) -> dict[str, list[dict[str, str]]]:
        """
        Формирует контент для Gigachat с изображениями.

        Args:
            images_ids: Список ID изображений

        Returns:
            Контент для отправки в Gigachat
        """
        payload = {
            "messages": [{"role": "user", "content": self.prompt}],
        }
        print("_content_for_gigachat.images_ids", images_ids)
        for img_id in images_ids:
            payload["messages"].append(
                {"role": "user", "type": "file", "file_id": img_id}
            )

        print("_payload_for_gigachat.payload")
        pprint(payload)

        payload_via_chat = Chat(
            messages=[
                Messages(role="user", content=self.prompt),
                *[
                    Messages(role="user", type="file", file_id=file_id)
                    for file_id in images_ids
                ],
            ],
        )

        return payload

    def _upload_photo_to_gigachat(self, images_bytes) -> List[str]:
        """
        Загружает и сохраняет фотографии в хранилище Gigachat

        Args:
             images_bytes: Список изображений в виде байтов

        Returns:
            saved_ids: List[int] Список ID сохраненных фотографий
        """
        saved_ids = []
        for image_bytes in images_bytes:
            uploaded_file = self._client.upload_file(file=image_bytes)
            saved_ids.append(uploaded_file.id_)
        return saved_ids

    @staticmethod
    def _extract_json_from_response(response: str) -> List[dict[str, Any]]:
        """
        Извлекает JSON из ответа модели.

        Args:
            response: Ответ модели

        Returns:
            Список словарей с данными
        """
        json_match = re.search(r"\[.*\]", response, re.DOTALL)

        if json_match:
            json_str = json_match.group()
        else:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = f"[{json_match.group()}]"
            else:
                json_str = response

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
