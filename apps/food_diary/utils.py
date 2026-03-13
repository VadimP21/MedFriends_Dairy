from datetime import time
import functools

from django.core.cache import cache
from django.http import Http404
from django.core.exceptions import ValidationError
from django.db import OperationalError, IntegrityError

from apps.food_diary.base import (
    ValidationErrorResponse,
    ErrorResponse,
    NotFoundResponse,
)
from apps.food_diary.models import MealTimeSlot
from apps.food_diary.models import Meal


def get_meal_name_by_time(timestamp: time) -> str:
    """
    Определить тип приема пищи по времени с использованием кэша
    """
    # Пытаемся получить слоты из кэша
    slots = cache.get("meal_time_slots")

    if slots is None:
        # Если в кэше нет, берем из БД и сохраняем в кэш на 24 часа
        slots = list(MealTimeSlot.objects.all().order_by("start_hour"))
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


def errors_normalized():
    """
    Декоратор для отлавливания и выдачи ошибок в роуты
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValidationError as e:
                return 400, ValidationErrorResponse(
                    error="Validation error",
                    detail=e.message,
                    field_errors=getattr(e, "message_dict", None),
                )
            except PermissionError:
                return 403, ErrorResponse(
                    error="Permission denied",
                    detail="You don't have permission to view meals",
                )
            except IntegrityError as e:
                if "unique constraint" in str(e).lower():
                    return 409, ErrorResponse(
                        error="Conflict",
                        detail="A meal with these parameters already exists",
                    )
            except Http404:
                return 404, NotFoundResponse(
                    error="Not found",
                    detail=f"Meal with id {kwargs.get("meal_id") or kwargs.get("payload").id} not found",
                )
            except OperationalError as e:
                if "database is locked" in str(e).lower():
                    return 503, ErrorResponse(
                        error="Database busy",
                        detail="The database is currently locked. Please try again.",
                    )
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Unexpected error in create_meal: {e}", exc_info=True)

                return 500, ErrorResponse(
                    error="Internal server error", detail="An unexpected error occurred"
                )

        return wrapper

    return decorator
