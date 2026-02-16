import uuid
from datetime import time

from django.core.cache import cache

from apps.food_diary.models import MealTimeSlot
from typing import Tuple, Union


def get_meal_name_by_time(timestamp: time):
    slots = cache.get("meal_time_slots")

    if slots is None:
        # Если в кэше нет, берем из БД и сохраняем в кэш на 24 часа
        slots = list(MealTimeSlot.objects.all())
        cache.set("meal_time_slots", slots, 60 * 60 * 24)

    hour = timestamp.hour

    for slot in slots:
        if slot.start_hour <= hour < slot.end_hour:
            return slot.get_title_display().lower()

    return "перекус"


def parse_uuid(uuid_str: str) -> Tuple[bool, Union[str, str]]:
    """
    Парсит UUID в любом формате

    Returns:
        (is_valid, result) где result - либо ошибка, либо нормализованный UUID
    """
    if not uuid_str:
        return False, "UUID cannot be empty"

    clean = uuid_str.replace('-', '')

    if len(clean) != 32:
        return False, f"Invalid UUID length: {len(clean)}. Expected 32 characters."

    try:
        int(clean, 16)
    except ValueError:
        return False, f"Invalid UUID format: {uuid_str}. Must contain only hex characters."

    # Форматируем с дефисами
    formatted = f"{clean[0:8]}-{clean[8:12]}-{clean[12:16]}-{clean[16:20]}-{clean[20:32]}"

    try:
        uuid.UUID(formatted)
    except ValueError as e:
        return False, f"Invalid UUID: {e}"

    return True, formatted