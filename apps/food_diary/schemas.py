import datetime
import typing as t
from uuid import UUID
from ninja import Schema
from pydantic import Field, field_validator, ConfigDict


class DishBaseIn(Schema):
    """Базовая схема блюда"""
    name: str = Field(..., max_length=200)
    weight: float = Field(..., ge=0.0, le=10000.0)
    calories: int = Field(..., ge=0, le=10000)
    protein: float = Field(..., ge=0.0, le=100.0)
    fat: float = Field(..., ge=0.0, le=100.0)
    carbohydrates: float = Field(..., ge=0.0, le=100.0)
    score: float = Field(..., ge=0.0, le=1.0)
    description: t.Optional[str] = Field(None, max_length=200)


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
    score: float
    description: t.Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class MealBaseIn(Schema):
    """Базовая схема приема пищи"""
    name: t.Optional[str] = Field(None, description="breakfast/lunch/dinner/snack")
    meal_date: datetime.date = Field(default_factory=lambda: datetime.datetime.now().date(), description="Дата приема пищи")
    meal_time: datetime.time = Field(default_factory=lambda: datetime.datetime.now().time(), description="Время приема пищи")
    portion_size: str = Field(..., description="Текстовое описание размера порции")
    description: t.Optional[str] = Field(None, max_length=200)
    components: list[DishCreateIn] = Field(..., min_length=1)

    @field_validator('name')
    def validate_meal_type(cls, v):
        allowed = ['breakfast', 'lunch', 'dinner', 'snack']
        if v not in allowed:
            raise ValueError(f'meal_name must be one of {allowed}')
        return v


class MealCreateIn(MealBaseIn):
    """Создание приема пищи"""
    pass


class MealUpdateIn(Schema):
    """Обновление приема пищи (все опционально)"""
    id: UUID
    name: t.Optional[str] = Field(None, description="breakfast/lunch/dinner/snack")
    meal_date: t.Optional[datetime.date] = Field(None, description="Дата приема пищи")
    meal_time: t.Optional[datetime.time] = Field(None, description="Время приема пищи")
    portion_size: t.Optional[str] = Field(None, description="Текстовое описание размера порции")
    description: t.Optional[str] = Field(None, max_length=200, description="Описание")
    components: t.Optional[list[DishCreateIn]] = Field(None, description="Список блюд")

    @field_validator('name')
    def validate_meal_type(cls, v):
        allowed = ['breakfast', 'lunch', 'dinner', 'snack']
        if v not in allowed:
            raise ValueError(f'meal_name must be one of {allowed}')
        return v

class MealOut(Schema):
    """Ответ с данными приема пищи"""
    id: UUID
    patient_id: UUID
    name: str
    meal_date: datetime.date
    meal_time: datetime.time
    portion_size: str
    description: t.Optional[str]
    components: list[DishOut]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Вычисляемые поля
    total_weight: float
    total_calories: int
    total_protein: float
    total_fat: float
    total_carbohydrates: float
    avg_score: float

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