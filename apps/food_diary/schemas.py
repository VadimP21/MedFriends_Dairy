import datetime
import typing as t
from uuid import UUID
from ninja import Schema
from pydantic import Field, field_validator, ConfigDict

from .models import Meal


class DishBaseIn(Schema):
    """Базовая схема блюда"""
    name: str = Field(..., max_length=200, description="Название блюда")
    weight: float = Field(..., ge=0.0, le=10000.0, description="Вес в граммах")
    calories: int = Field(..., ge=0, description="Калорийность")
    protein: float = Field(..., ge=0.0, description="Белки в граммах")
    fat: float = Field(..., ge=0.0, description="Жиры в граммах")
    carbohydrates: float = Field(..., ge=0.0, description="Углеводы в граммах")


class DishCreateIn(DishBaseIn):
    """Создание блюда"""
    pass


class DishOut(Schema):
    """Ответ с данными блюда"""
    id: UUID
    name: str
    weight: float
    calories: int
    protein: float
    fat: float
    carbohydrates: float
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class MealBaseIn(Schema):
    """Базовая схема приема пищи"""
    name: t.Optional[str] = Field(None, description="Завтрак, обед, ужин, перекус")
    meal_date: datetime.date = Field(default_factory=lambda: datetime.datetime.now().date(),
                                     description="Дата приема пищи")
    meal_time: datetime.time = Field(default_factory=lambda: datetime.datetime.now().time(),
                                     description="Время приема пищи")
    components: list[DishCreateIn] = Field(..., min_length=1, description="Блюда в приеме пищи")

    @field_validator('name')
    def validate_meal_type(cls, v: str):
        if v.lower() not in Meal.MealTypes.values:
            raise ValueError(f'meal_name must be one of {Meal.MealTypes.values}')
        return v.lower()


class MealCreateIn(MealBaseIn):
    """Создание приема пищи"""
    pass


class MealUpdateIn(Schema):
    """Обновление приема пищи (все опционально)"""
    id: UUID
    name: t.Optional[str] = Field(None, description="breakfast/lunch/dinner/snack")
    meal_date: t.Optional[datetime.date] = Field(None, description="Дата приема пищи")
    meal_time: t.Optional[datetime.time] = Field(None, description="Время приема пищи")
    components: t.Optional[list[DishCreateIn]] = Field(None, description="Список блюд")

    @field_validator('name')
    def validate_meal_type(cls, v: str):
        if v.lower() not in Meal.MealTypes.values:
            raise ValueError(f'meal_name must be one of {Meal.MealTypes.values}')
        return v.lower()


class MealOut(Schema):
    """Ответ с данными приема пищи"""
    id: UUID
    patient_id: UUID
    name: str
    meal_date: datetime.date
    meal_time: datetime.time
    components: list[DishOut]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Вычисляемые поля
    total_weight: float
    total_calories: int
    total_protein: float
    total_fat: float
    total_carbohydrates: float

    model_config = ConfigDict(from_attributes=True)


class MealsResponse(Schema):
    """Расширенная версия ответа со списком MealOut"""

    model_config = ConfigDict(from_attributes=True)

    name: str = "meal"
    components: t.Optional[list[MealOut]] = None


class MealListOut(Schema):
    """Краткий ответ для списка приемов пищи"""
    id: UUID
    name: str
    meal_date: datetime.date
    meal_time: datetime.time
    total_calories: int
    components_count: int

    model_config = ConfigDict(from_attributes=True)


class DailySummaryOut(Schema):
    """Сводка за день"""
    date: datetime.date
    total_meals: int
    total_calories: int
    total_protein: float
    total_fat: float
    total_carbohydrates: float
    by_meal_type: dict[str, dict[str, float]]
