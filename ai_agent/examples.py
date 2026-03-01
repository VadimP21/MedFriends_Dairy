"""
Примеры использования сервиса анализа еды с изображениями.
"""

import asyncio
import logging
import os

from .food_analysis_service import food_analysis_service, FoodAnalysisService
from .openai_vision_client import OpenAIVisionLLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_with_url():
    """Пример анализа еды по URL изображения."""
    
    # URL изображений с едой (примеры)
    food_images = [
        "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445",  # Блинчики
        "https://images.unsplash.com/photo-1551024601-bec78aea704b",  # Донут
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"   # Салат
    ]
    
    print("=" * 60)
    print("Пример 1: Анализ одного изображения")
    print("=" * 60)
    
    # Анализируем первое изображение
    result = await food_analysis_service.analyze_food_image(
        food_images[0],
        additional_context="Это завтрак, порция средняя"
    )
    
    print(f"Блюдо: {result.food_name}")
    print(f"Калории: {result.calories} ккал")
    print(f"Белки: {result.proteins} г")
    print(f"Жиры: {result.fats} г")
    print(f"Углеводы: {result.carbohydrates} г")
    print(f"Уверенность: {result.confidence:.1%}")
    print(f"Порция: {result.portion_size}")
    
    if result.ingredients:
        print("Ингредиенты:")
        for ing in result.ingredients:
            print(f"  - {ing.get('name')}: {ing.get('portion', 'по вкусу')}")
    
    print("\n" + "=" * 60)
    print("Пример 2: Полный JSON ответ")
    print("=" * 60)
    print(result.to_json())
    
    print("\n" + "=" * 60)
    print("Пример 3: Анализ нескольких изображений")
    print("=" * 60)
    
    results = await food_analysis_service.analyze_multiple_food_images(
        food_images[:2],  # Анализируем первые два
        additional_context="Обед из двух блюд"
    )
    
    total_calories = 0
    for i, r in enumerate(results, 1):
        print(f"\nБлюдо {i}: {r.food_name}")
        print(f"  Калории: {r.calories} ккал")
        total_calories += r.calories
    
    print(f"\nСуммарная калорийность: {total_calories} ккал")


async def example_with_meal_context():
    """Пример с контекстом приема пищи."""
    
    print("\n" + "=" * 60)
    print("Пример 4: Анализ с контекстом приема пищи")
    print("=" * 60)
    
    # URL изображения
    pizza_url = "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38"  # Пицца
    
    # Анализ с указанием типа приема пищи
    result = await food_analysis_service.analyze_with_estimation(
        pizza_url,
        meal_type="lunch"
    )
    
    print(f"Тип приема пищи: {result['meal_type']}")
    print(f"Блюдо: {result['food_name']}")
    print(f"КБЖУ: {result['nutrition']}")
    print(f"Вклад в дневную норму:")
    for key, value in result['daily_contribution'].items():
        print(f"  {key}: {value}%")
    
    print("Рекомендации:")
    for rec in result['recommendations']:
        print(f"  • {rec}")


async def example_with_local_image():
    """Пример с локальным файлом изображения."""
    
    print("\n" + "=" * 60)
    print("Пример 5: Анализ локального изображения")
    print("=" * 60)
    
    # Здесь должен быть путь к локальному файлу
    local_image_path = "path/to/your/food_photo.jpg"
    
    # Проверяем, существует ли файл
    if os.path.exists(local_image_path):
        with open(local_image_path, "rb") as f:
            image_bytes = f.read()
        
        result = await food_analysis_service.analyze_food_image(
            image_bytes,
            additional_context="Домашняя еда"
        )
        
        print(f"Блюдо: {result.food_name}")
        print(f"Калории: {result.calories} ккал")
    else:
        print(f"Файл {local_image_path} не найден. Пропускаем пример с локальным файлом.")
        
        # Демонстрация работы с байтами (генерируем тестовые данные)
        print("Демонстрация работы с байтами (тестовый режим):")
        
        # Создаем тестовый клиент, который не требует реального API
        class TestVisionClient(OpenAIVisionLLMClient):
            async def ainvoke_with_images(self, prompt, images, **kwargs):
                # Имитируем ответ модели
                return '''
                {
                    "food_name": "Тестовое блюдо: Омлет с овощами",
                    "nutrition": {
                        "calories": 320,
                        "proteins": 18,
                        "fats": 22,
                        "carbohydrates": 12
                    },
                    "portion_size": "2 яйца с помидорами",
                    "confidence": 0.95,
                    "ingredients": [
                        {"name": "яйца", "portion": "2 шт"},
                        {"name": "помидоры", "portion": "50 г"},
                        {"name": "лук", "portion": "20 г"},
                        {"name": "масло оливковое", "portion": "10 г"}
                    ]
                }
                '''
        
        # Используем тестовый клиент
        test_service = FoodAnalysisService(TestVisionClient())
        test_bytes = b"fake_image_bytes"
        
        result = await test_service.analyze_food_image(test_bytes)
        print(f"Блюдо: {result.food_name}")
        print(f"Калории: {result.calories} ккал")
        print(f"Уверенность: {result.confidence:.1%}")
        print(f"Ингредиенты: {[i['name'] for i in result.ingredients]}")


async def example_custom_prompt():
    """Пример с кастомным промптом."""
    
    print("\n" + "=" * 60)
    print("Пример 6: Кастомный запрос (определение остроты)")
    print("=" * 60)
    
    # URL изображения
    spicy_food = "https://images.unsplash.com/photo-1589301760014-d929f3979dbc"  # Острая еда
    
    # Создаем кастомный клиент с другим промптом
    custom_prompt = """
    Определи название блюда и оцени его остроту по шкале от 1 до 10.
    Верни JSON в формате:
    {
        "food_name": "название",
        "spiciness_level": число от 1 до 10,
        "main_spicy_ingredients": ["ингредиент1", "ингредиент2"]
    }
    """
    
    class CustomPromptClient(OpenAIVisionLLMClient):
        async def ainvoke_with_images(self, prompt, images, **kwargs):
            # В реальном коде здесь был бы вызов API
            # А пока - имитация ответа
            return '''
            {
                "food_name": "Том Ям",
                "shpiciness_level": 8,
                "main_spicy_ingredients": ["перец чили", "галангал", "лемонграсс"]
            }
            '''
    
    custom_client = CustomPromptClient()
    custom_service = FoodAnalysisService(custom_client)
    
    # Отправляем кастомный запрос
    response = await custom_client.ainvoke_with_images(custom_prompt, [spicy_food])
    print(response)


async def main():
    """Запуск всех примеров."""
    
    print("СЕРВИС АНАЛИЗА ФОТОГРАФИЙ ЕДЫ С КБЖУ")
    print("Используется мультимодальный AI Vision\n")
    
    try:
        await example_with_url()
        await example_with_meal_context()
        await example_with_local_image()
        await example_custom_prompt()
    except Exception as e:
        logger.error("Ошибка в примере: %s", str(e))
        print(f"\nПроизошла ошибка: {e}")
        print("Убедитесь, что установлен API ключ OpenAI и есть доступ к Vision API")


if __name__ == "__main__":
    asyncio.run(main())