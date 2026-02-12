from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict, computed_field


class DishBase(BaseModel):
    """Базовая схема блюда"""

    name: str = Field(..., max_length=200)

    weight: float = Field(..., ge=0.0, le=10000.0, description="Вес продукта в граммах")
    calories: int = Field(
        ..., ge=0, le=10000, description="Количество калорий в указанном весе"
    )
    protein: float = Field(
        ..., ge=0.0, le=100.0, description="Количество белков в указанном весе"
    )
    fat: float = Field(
        ..., ge=0.0, le=100.0, description="Количество жиров в указанном весе"
    )
    carbohydrates: float = Field(
        ..., ge=0.0, le=100.0, description="Количество углеводов в указанном весе"
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Индекс «здорового питания»")

    description: str | None = Field(
        None, max_length=200, description="Средний размер порции в граммах"
    )


class DishCreate(DishBase):
    """Схема для создания блюда"""

    pass


class DishUpdate(DishBase):
    """Схема для создания блюда"""

    pass


class DishResponse(DishBase):
    """Схема для отображения блюда"""

    id: int

    model_config = ConfigDict(from_attributes=True)
