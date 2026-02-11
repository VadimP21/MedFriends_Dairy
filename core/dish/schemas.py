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


class DishRead(DishBase):
    """Схема для отображения блюда"""

    id: int

    model_config = ConfigDict(from_attributes=True)


class MealBase(BaseModel):
    """Базовая схема приема пищи"""

    name: str | None = Field(None, description="Завтрак, Обед и т.д.")


class MealCreate(MealBase):
    """Схема для создания приема пищи"""

    user_id: int


class MealRead(MealBase):
    """Полная схема приема пищи со всеми продуктами и расчетами"""

    id: int
    user_id: int
    created_at: datetime
    components: List[DishRead] = []

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    def total_weight(self) -> float:
        return sum(item.weight for item in self.components)

    @computed_field
    def total_calories(self) -> int:
        return sum(item.calories for item in self.components)

    @computed_field
    def total_protein(self) -> float:
        return sum(item.protein for item in self.components)

    @computed_field
    def total_fat(self) -> float:
        return sum(item.fat for item in self.components)

    @computed_field
    def total_carbohydrates(self) -> float:
        return sum(item.carbohydrates for item in self.components)

    @computed_field
    def avg_score(self) -> float:
        if not self.components:
            return 0.0
        return sum(item.score for item in self.components) / len(self.components)
