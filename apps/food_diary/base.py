from ninja import Schema
from typing import Optional

from apps.food_diary.schemas import MealsResponse


# Схемы для ответов с ошибками
class ErrorResponse(Schema):
    """Стандартный ответ с ошибкой"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None  # Код ошибки для клиента


class ValidationErrorResponse(Schema):
    """Ошибка валидации данных"""
    success: bool = False
    error: str = "Validation error"
    detail: Optional[str] = None
    field_errors: Optional[dict[str, list[str]]] = None  # Ошибки по полям


class NotFoundResponse(Schema):
    """Ресурс не найден"""
    success: bool = False
    error: str = "Not found"
    detail: str


class SuccessResponse(Schema):
    """Базовый успешный ответ"""
    success: bool = True
    message: str


# Схемы для успешных ответов
class CreateMealSuccessResponse(Schema):
    """Успешное создание приема пищи"""
    success: bool = True
    message: str = "Meal created successfully"
    data: MealsResponse


class UpdateMealSuccessResponse(Schema):
    """Успешное обновление приема пищи"""
    success: bool = True
    message: str = "Meal updated successfully"
    data: MealsResponse


class GetMealSuccessResponse(Schema):
    """Успешное получение приема пищи"""
    success: bool = True
    data: MealsResponse


class GetMealsSuccessResponse(Schema):
    """Успешное получение списка приемов пищи"""
    success: bool = True
    data: MealsResponse
    count: int
    filters: Optional[dict] = None


class DeleteMealSuccessResponse(Schema):
    """Успешное удаление приема пищи"""
    success: bool = True
    message: str = "Meal deleted successfully"
    deleted_id: str

