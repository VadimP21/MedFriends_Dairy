import uuid
from datetime import time
from typing import Tuple, Union

from django.core.cache import cache

from apps.food_diary.models import MealTimeSlot
from apps.food_diary.models import Meal, Dish


def get_meal_name_by_time(timestamp: time) -> str:
    """
    Определить тип приема пищи по времени с использованием кэша
    """
    # Пытаемся получить слоты из кэша
    slots = cache.get("meal_time_slots")

    if slots is None:
        # Если в кэше нет, берем из БД и сохраняем в кэш на 24 часа
        slots = list(MealTimeSlot.objects.all().order_by('start_hour'))
        cache.set("meal_time_slots", slots, 60 * 60 * 24)  # 24 часа

    hour = timestamp.hour

    # Ищем подходящий слот
    for slot in slots:
        # Обрабатываем случаи, когда интервал переходит через полночь
        if slot.start_hour <= slot.end_hour:
            # Обычный интервал (например, 6-10)
            if slot.start_hour <= hour < slot.end_hour:
                return slot.get_title_display().lower()
        else:
            # Интервал через полночь (например, 22-6)
            if hour >= slot.start_hour or hour < slot.end_hour:
                return slot.get_title_display().lower()

    return Meal.MealTypes.SNACK
