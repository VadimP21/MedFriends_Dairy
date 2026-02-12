import pytest
from pydantic import ValidationError

from core.food_dairy.schemas.schemas import DishCreate
from core.food_dairy.tests.fixtures import TestDishFixture


class TestDish(TestDishFixture):
    """
    ТЕСТ ДЕКОРАТОРА И VIEW (Integration)

    """

    def test_dish_schema_validation(self, dish_create_data, invalid_data):
        """Проверяем, что Pydantic правильно валидирует данные"""

        dish = DishCreate.model_validate(dish_create_data)
        assert dish.name == "Хлеб цельнозерновой тост"

        with pytest.raises(ValidationError):
            DishCreate.model_validate(invalid_data)
