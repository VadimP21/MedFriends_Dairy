# apps/food/tests/test_schemas.py
import pytest
import datetime
import uuid
from pydantic import ValidationError

from apps.food_diary.schemas import (
    DishCreateIn, DishOut,
    MealCreateIn, MealUpdateIn, MealOut, MealListOut,
    DailySummaryOut
)


class TestDishSchemas:
    """Тесты для схем блюд"""

    def test_dish_create_in_valid(self):
        """Тест валидных данных для создания блюда"""
        data = {
            "name": "Омлет",
            "weight": 200,
            "calories": 350,
            "protein": 20,
            "fat": 25,
            "carbohydrates": 5,
            "score": 0.8,
            "description": "Тестовое описание"
        }

        dish = DishCreateIn(**data)
        assert dish.name == "Омлет"
        assert dish.weight == 200

    def test_dish_create_in_invalid_weight(self):
        """Тест невалидного веса"""
        data = {
            "name": "Омлет",
            "weight": 20000,  # > 10000
            "calories": 350,
            "protein": 20,
            "fat": 25,
            "carbohydrates": 5,
            "score": 0.8
        }

        with pytest.raises(ValidationError) as exc:
            DishCreateIn(**data)
        assert "weight" in str(exc.value)

    def test_dish_create_in_invalid_score(self):
        """Тест невалидного score"""
        data = {
            "name": "Омлет",
            "weight": 200,
            "calories": 350,
            "protein": 20,
            "fat": 25,
            "carbohydrates": 5,
            "score": 1.5  # > 1.0
        }

        with pytest.raises(ValidationError) as exc:
            DishCreateIn(**data)
        assert "score" in str(exc.value)

    def test_dish_out_serialization(self, meal):
        """Тест сериализации DishOut"""
        from apps.food_diary.models import Dish
        dish = Dish.objects.create(
            meal=meal,
            name="Омлет",
            weight=200,
            calories=350,
            protein=20,
            fat=25,
            carbohydrates=5,
            score=0.8
        )

        dish_out = DishOut.from_orm(dish)
        assert dish_out.id == dish.id
        assert isinstance(dish_out.id, str)  # UUID сериализован в строку
        assert dish_out.name == "Омлет"


class TestMealSchemas:
    """Тесты для схем приемов пищи"""

    def test_meal_create_in_valid(self, meal_data):
        """Тест валидных данных для создания приема пищи"""
        meal = MealCreateIn(**meal_data)

        assert meal.meal_type == "breakfast"
        assert len(meal.components) == 2
        assert meal.components[0].name == "Омлет"

    def test_meal_create_in_invalid_meal_type(self, meal_data):
        """Тест невалидного типа приема пищи"""
        meal_data["meal_type"] = "invalid"

        with pytest.raises(ValidationError) as exc:
            MealCreateIn(**meal_data)
        assert "meal_type" in str(exc.value)

    def test_meal_create_in_empty_components(self, meal_data):
        """Тест пустого списка компонентов"""
        meal_data["components"] = []

        with pytest.raises(ValidationError) as exc:
            MealCreateIn(**meal_data)
        assert "components" in str(exc.value)

    def test_meal_update_in_valid(self):
        """Тест валидных данных для обновления"""
        data = {
            "id": str(uuid.uuid4()),
            "meal_type": "lunch",
            "name": "Обед"
        }

        meal = MealUpdateIn(**data)
        assert meal.meal_type == "lunch"
        assert meal.meal_date is None

    def test_meal_out_from_orm(self, meal):
        """Тест создания MealOut из ORM объекта"""
        meal_out = MealOut.from_orm(meal)

        assert meal_out.id == meal.id
        assert isinstance(meal_out.id, str)
        assert meal_out.meal_type == meal.meal_type
        assert len(meal_out.components) == meal.components.count()

    def test_meal_list_out_from_orm(self, meal):
        """Тест создания MealListOut из ORM объекта"""
        meal_list = MealListOut.from_orm(meal)

        assert meal_list.id == meal.id
        assert meal_list.total_calories == meal.total_calories
        assert meal_list.components_count == meal.components.count()


class TestDailySummarySchema:
    """Тесты для схемы сводки за день"""

    def test_daily_summary_out(self):
        """Тест создания сводки"""
        data = {
            "date": datetime.date.today(),
            "total_meals": 3,
            "total_calories": 1200,
            "total_protein": 60,
            "total_fat": 40,
            "total_carbohydrates": 120,
            "by_meal_type": {
                "breakfast": {"count": 1, "calories": 400},
                "lunch": {"count": 1, "calories": 500},
                "dinner": {"count": 1, "calories": 300}
            }
        }

        summary = DailySummaryOut(**data)
        assert summary.total_meals == 3
        assert summary.by_meal_type["breakfast"]["calories"] == 400