import pytest
from pydantic import ValidationError

from core.food_dairy.schemas.meal_schemas import MealCreate
from core.food_dairy.tests.tests_meal.test_meal_fixtures import TestMealFixture


class TestMeal(TestMealFixture):
    """
    ТЕСТ ДЕКОРАТОРА И VIEW (Integration)

    """

    def test_meal_schema_validation(self, meal_create_data, invalid_data):
        """Проверяем, что Pydantic правильно валидирует данные"""

        meal = MealCreate.model_validate(meal_create_data)
        print("!@!@!@!@!@!@!@!@!@", meal)

        assert meal.name == "Завтрак"

        with pytest.raises(ValidationError):
            MealCreate.model_validate(invalid_data)
