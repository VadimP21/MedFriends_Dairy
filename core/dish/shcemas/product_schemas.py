from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from pydantic import BaseModel, Field


class ProductBasic(BaseModel):
    """Базовая схема продукта без категории"""

    name: str = Field(..., max_length=200)
    average_portion: int = Field(
        default=100, ge=1, le=10000, description="Средний размер порции в граммах"
    )
    description: str | None = Field(
        None, max_length=200, description="Средний размер порции в граммах"
    )
    calories: int = Field(..., ge=0, le=10000, description="Калории на 100 грамм")
    protein: float = Field(..., ge=0.0, le=100.0, description="Белки на 100 грамм")
    fat: float = Field(..., ge=0.0, le=100.0, description="Жиры на 100 грамм")
    carbohydrates: float = Field(
        ..., ge=0.0, le=100.0, description="Углеводы на 100 грамм"
    )


class ProductCreate(BaseModel):
    """Схема для создания продукта"""

    pass


class ProductUpdate(BaseModel): ...


class ProductResponse(BaseModel):
    """Схема для ответа с продуктом"""

    ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime
