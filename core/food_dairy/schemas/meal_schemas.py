from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict, computed_field, field_validator

from core.food_dairy.schemas.dish_schemas import DishBase


class MealBase(BaseModel):
    """Базовая схема приема пищи"""

    name: str | None = Field(
        default=None, max_length=100, description="Завтрак, Обед и т.д."
    )
    created_at: datetime = Field(default_factory=datetime.now)
    portion_size: str = Field(
        default=None, description="Текстовое описание размера порции"
    )
    description: str | None = Field(default=None, max_length=200)
    components: List[DishBase] = Field(..., min_length=1)


class MealCreate(MealBase):
    """Схема для создания приема пищи"""

    pass


class MealUpdate(MealBase):
    id: int
    # name: str | None = None
    # portion_size: str | None = None
    # # created_at: datetime | None = None
    # description: str | None = None
    components: List[DishBase] | None = None


class MealResponse(MealBase):
    """Схема для ответа по приему пищи"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime

    @field_validator("components", mode="before")
    @classmethod
    def convert_related_manager(cls, v):
        """
        Автоматически вызывает .all(),
        если видит менеджер Django
        """
        if hasattr(v, "all"):
            return list(v.all())
        return v

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
        return round(
            sum(item.score for item in self.components) / len(self.components), 2
        )


class MealShortResponse(BaseModel):
    """Краткая версия ответа (например, для списка приемов пищи без деталей)"""

    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AllMealsResponse(BaseModel):
    """Расширенная версия ответа со списком MealResponse"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    components: List[MealResponse] | None
