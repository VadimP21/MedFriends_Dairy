"""
Модуль с сервисом для анализа фотографий еды и расчета КБЖУ.
"""

import logging
import json
import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from .base import BaseLLMClient
from .openai_vision_client import OpenAIVisionLLMClient
from .service import LLMService

logger = logging.getLogger(__name__)


class FoodNutritionInfo:
    """Модель данных для информации о питании."""
    
    def __init__(
        self,
        food_name: str,
        calories: float,
        proteins: float,
        fats: float,
        carbohydrates: float,
        portion_size: Optional[str] = None,
        confidence: float = 0.8,
        ingredients: Optional[List[Dict[str, Any]]] = None
    ):
        self.food_name = food_name
        self.calories = calories
        self.proteins = proteins
        self.fats = fats
        self.carbohydrates = carbohydrates
        self.portion_size = portion_size
        self.confidence = confidence
        self.ingredients = ingredients or []
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует в словарь."""
        return {
            "food_name": self.food_name,
            "nutrition": {
                "calories": self.calories,
                "proteins": self.proteins,
                "fats": self.fats,
                "carbohydrates": self.carbohydrates
            },
            "portion_size": self.portion_size,
            "confidence": self.confidence,
            "ingredients": self.ingredients,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """Преобразует в JSON строку."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str):
        """Создает объект из JSON строки."""
        data = json.loads(json_str)
        return cls(
            food_name=data["food_name"],
            calories=data["nutrition"]["calories"],
            proteins=data["nutrition"]["proteins"],
            fats=data["nutrition"]["fats"],
            carbohydrates=data["nutrition"]["carbohydrates"],
            portion_size=data.get("portion_size"),
            confidence=data.get("confidence", 0.8),
            ingredients=data.get("ingredients", [])
        )


class FoodAnalysisService:
    """
    Сервис для анализа фотографий еды и расчета КБЖУ.
    Использует мультимодальный LLM клиент.
    """
    
    # Системный промпт для анализа еды
    FOOD_ANALYSIS_SYSTEM_PROMPT = """
Ты - эксперт-диетолог с глубокими знаниями о составе блюд и их пищевой ценности.
Твоя задача - анализировать фотографии еды и предоставлять точную информацию о КБЖУ.

Правила анализа:
1. Определи название блюда максимально точно
2. Оцени примерный размер порции
3. Рассчитай КБЖУ (калории, белки, жиры, углеводы) на основе:
   - Типичного состава блюда
   - Размера порции
   - Стандартных рецептур
4. Если можешь определить ингредиенты, перечисли их с примерными пропорциями
5. Укажи уровень уверенности в оценке (0.0-1.0)

Верни результат строго в формате JSON со следующей структурой:
{
    "food_name": "название блюда",
    "nutrition": {
        "calories": число (ккал),
        "proteins": число (г),
        "fats": число (г),
        "carbohydrates": число (г)
    },
    "portion_size": "описание размера порции",
    "confidence": число от 0 до 1,
    "ingredients": [
        {"name": "ингредиент", "portion": "примерное количество"}
    ]
}

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
        self._llm_service = LLMService(self._client)
        
        logger.info(
            "Инициализирован FoodAnalysisService с клиентом: %s",
            self._client.__class__.__name__
        )
    
    async def analyze_food_image(
        self,
        image: Union[str, bytes],
        additional_context: Optional[str] = None
    ) -> FoodNutritionInfo:
        """
        Анализирует одно изображение еды.
        
        Args:
            image: URL изображения или байты
            additional_context: Дополнительный контекст (например, "это обед", "порция большая")
        
        Returns:
            FoodNutritionInfo с данными о КБЖУ
        """
        prompt = self._build_analysis_prompt(additional_context)
        
        try:
            response = await self._client.ainvoke_with_images(
                prompt=prompt,
                images=[image],
                temperature=0.2,  # Низкая температура для точности
                max_tokens=1000
            )
            
            # Извлекаем JSON из ответа
            nutrition_data = self._extract_json_from_response(response)
            
            # Создаем объект с данными
            return FoodNutritionInfo(
                food_name=nutrition_data.get("food_name", "Неизвестное блюдо"),
                calories=nutrition_data.get("nutrition", {}).get("calories", 0),
                proteins=nutrition_data.get("nutrition", {}).get("proteins", 0),
                fats=nutrition_data.get("nutrition", {}).get("fats", 0),
                carbohydrates=nutrition_data.get("nutrition", {}).get("carbohydrates", 0),
                portion_size=nutrition_data.get("portion_size"),
                confidence=nutrition_data.get("confidence", 0.5),
                ingredients=nutrition_data.get("ingredients", [])
            )
            
        except Exception as e:
            logger.error("Ошибка при анализе изображения: %s", str(e))
            raise
    
    async def analyze_multiple_food_images(
        self,
        images: List[Union[str, bytes]],
        additional_context: Optional[str] = None
    ) -> List[FoodNutritionInfo]:
        """
        Анализирует несколько изображений еды (например, несколько блюд).
        
        Args:
            images: Список изображений
            additional_context: Дополнительный контекст
        
        Returns:
            Список FoodNutritionInfo для каждого изображения
        """
        results = []
        
        for i, image in enumerate(images):
            logger.info("Анализ изображения %d из %d", i + 1, len(images))
            try:
                result = await self.analyze_food_image(image, additional_context)
                results.append(result)
            except Exception as e:
                logger.error("Ошибка при анализе изображения %d: %s", i + 1, str(e))
                # Добавляем "пустой" результат с низкой уверенностью
                results.append(
                    FoodNutritionInfo(
                        food_name=f"Ошибка анализа {i+1}",
                        calories=0,
                        proteins=0,
                        fats=0,
                        carbohydrates=0,
                        confidence=0.0
                    )
                )
        
        return results
    
    async def analyze_with_estimation(
        self,
        image: Union[str, bytes],
        meal_type: Optional[str] = None  # breakfast, lunch, dinner, snack
    ) -> Dict[str, Any]:
        """
        Анализирует изображение и возвращает расширенную информацию
        с оценкой для дневного рациона.
        
        Args:
            image: Изображение еды
            meal_type: Тип приема пищи
        
        Returns:
            Словарь с данными анализа и рекомендациями
        """
        # Получаем базовый анализ
        nutrition = await self.analyze_food_image(image)
        
        # Добавляем контекстную информацию
        result = nutrition.to_dict()
        
        # Добавляем метаданные о приеме пищи
        result["meal_type"] = meal_type or "unknown"
        
        # Добавляем рекомендации (пример)
        result["recommendations"] = self._generate_recommendations(nutrition)
        
        # Добавляем оценку вклада в дневную норму (примерные значения)
        result["daily_contribution"] = {
            "calories_percent": round((nutrition.calories / 2000) * 100, 1),  # при норме 2000 ккал
            "proteins_percent": round((nutrition.proteins / 50) * 100, 1),    # примерная норма
            "fats_percent": round((nutrition.fats / 70) * 100, 1),
            "carbs_percent": round((nutrition.carbohydrates / 250) * 100, 1)
        }
        
        return result
    
    def _build_analysis_prompt(self, additional_context: Optional[str] = None) -> str:
        """Формирует промпт для анализа."""
        prompt = self.FOOD_ANALYSIS_SYSTEM_PROMPT
        
        if additional_context:
            prompt += f"\n\nДополнительная информация от пользователя: {additional_context}"
        
        prompt += "\n\nАнализируй изображение и верни JSON с данными о блюде."
        
        return prompt
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Извлекает JSON из ответа модели.
        
        Args:
            response: Ответ модели
        
        Returns:
            Словарь с данными
        """
        # Ищем JSON в ответе
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group()
        else:
            json_str = response
        
        # Пробуем распарсить
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Не удалось распарсить JSON, возвращаем пустой словарь")
            return {
                "food_name": "Не удалось распознать",
                "nutrition": {"calories": 0, "proteins": 0, "fats": 0, "carbohydrates": 0},
                "confidence": 0.1
            }
    
    def _generate_recommendations(self, nutrition: FoodNutritionInfo) -> List[str]:
        """
        Генерирует простые рекомендации на основе КБЖУ.
        
        Args:
            nutrition: Данные о питании
        
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Простые правила (пример)
        if nutrition.calories > 800:
            recommendations.append("Высококалорийное блюдо, возможно, стоит уменьшить порцию")
        
        if nutrition.fats > 30:
            recommendations.append("Много жиров, обратите внимание на баланс")
        
        if nutrition.proteins < 10 and nutrition.calories > 300:
            recommendations.append("Мало белка при такой калорийности")
        
        if nutrition.carbohydrates > 100:
            recommendations.append("Много углеводов, возможно, стоит выбрать другой гарнир")
        
        if not recommendations:
            recommendations.append("Сбалансированное блюдо")
        
        return recommendations


# Глобальный экземпляр сервиса
food_analysis_service = FoodAnalysisService()