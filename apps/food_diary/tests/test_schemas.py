# tests/unit/test_schemas.py

import pytest
import datetime
import uuid
from pydantic import ValidationError

from apps.food_diary.schemas import (
    DishBaseIn,
    DishCreateIn,
    DishOut,
    MealBaseIn,
    MealCreateIn,
    MealUpdateIn,
    MealOut,
    MealsResponse,
    MealListOut,
    DailySummaryOut,
)


class TestDishSchemas:
    """Тесты для схем блюд"""

    def test_dish_base_in_valid(self):
        """Тест валидной базовой схемы блюда"""
        data = {
            "name": "Овсянка",
            "weight": 200,
            "calories": 350,
            "protein": 12.5,
            "fat": 6.2,
            "carbohydrates": 60.1,
        }
        dish = DishBaseIn(**data)

        assert dish.name == "Овсянка"
        assert dish.weight == 200
        assert dish.calories == 350
        assert dish.protein == 12.5
        assert dish.fat == 6.2
        assert dish.carbohydrates == 60.1

    def test_dish_base_in_invalid_weight(self):
        """Тест невалидного веса (отрицательный)"""
        data = {
            "name": "Овсянка",
            "weight": -100,  # отрицательный вес
            "calories": 350,
            "protein": 12,
            "fat": 6,
            "carbohydrates": 60,
        }
        with pytest.raises(ValidationError) as exc:
            DishBaseIn(**data)
        assert "weight" in str(exc.value)

    def test_dish_base_in_weight_too_large(self):
        """Тест слишком большого веса (>10000)"""
        data = {
            "name": "Овсянка",
            "weight": 15000,  # > 10000
            "calories": 350,
            "protein": 12,
            "fat": 6,
            "carbohydrates": 60,
        }
        with pytest.raises(ValidationError) as exc:
            DishBaseIn(**data)
        assert "weight" in str(exc.value)

    def test_dish_base_in_missing_required(self):
        """Тест отсутствия обязательных полей"""
        data = {
            "name": "Овсянка",
            # пропущены обязательные поля
        }
        with pytest.raises(ValidationError) as exc:
            DishBaseIn(**data)
        assert "weight" in str(exc.value)
        assert "calories" in str(exc.value)

    def test_dish_create_in_inheritance(self):
        """Тест наследования DishCreateIn от DishBaseIn"""
        data = {
            "name": "Овсянка",
            "weight": 200,
            "calories": 350,
            "protein": 12,
            "fat": 6,
            "carbohydrates": 60,
        }
        dish = DishCreateIn(**data)
        assert dish.name == "Овсянка"
        assert isinstance(dish, DishBaseIn)

    def test_dish_out_creation(self):
        """Тест создания DishOut"""
        dish_id = uuid.uuid4()
        now = datetime.datetime.now()

        data = {
            "id": dish_id,
            "name": "Овсянка",
            "weight": 200,
            "calories": 350,
            "protein": 12.5,
            "fat": 6.2,
            "carbohydrates": 60.1,
            "created_at": now,
            "updated_at": now,
        }
        dish = DishOut(**data)

        assert dish.id == dish_id
        assert dish.name == "Овсянка"
        assert dish.created_at == now
        assert dish.updated_at == now

    def test_dish_out_config_from_attributes(self):
        """Тест наличия from_attributes в конфиге"""
        assert hasattr(DishOut, "model_config")
        assert isinstance(DishOut.model_config, dict)
        assert DishOut.model_config.get("from_attributes") is True


class TestMealSchemas:
    """Тесты для схем приемов пищи"""

    def test_meal_base_in_valid_with_name(self):
        """Тест валидной базовой схемы с именем"""
        data = {
            "name": "завтрак",
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            "components": [
                {
                    "name": "Овсянка",
                    "weight": 200,
                    "calories": 350,
                    "protein": 12,
                    "fat": 6,
                    "carbohydrates": 60,
                }
            ],
        }
        meal = MealBaseIn(**data)

        assert meal.name == "завтрак"
        assert len(meal.components) == 1
        assert meal.components[0].name == "Овсянка"

    def test_meal_base_in_valid_without_name(self):
        """Тест валидной базовой схемы без имени"""
        data = {
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            "components": [
                {
                    "name": "Овсянка",
                    "weight": 200,
                    "calories": 350,
                    "protein": 12,
                    "fat": 6,
                    "carbohydrates": 60,
                }
            ],
        }
        meal = MealBaseIn(**data)

        assert meal.name is None
        assert meal.meal_date == datetime.date.today()

    def test_meal_base_in_invalid_name(self):
        """Тест невалидного имени (не из списка MealTypes)"""
        data = {
            "name": "полдник",  # не из списка допустимых
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            "components": [
                {
                    "name": "Овсянка",
                    "weight": 200,
                    "calories": 350,
                    "protein": 12,
                    "fat": 6,
                    "carbohydrates": 60,
                }
            ],
        }
        with pytest.raises(ValidationError) as exc:
            MealBaseIn(**data)
        assert "meal_name must be one of" in str(exc.value)

    def test_meal_base_in_empty_components(self):
        """Тест пустого списка компонентов"""
        data = {
            "name": "завтрак",
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            "components": [],  # пустой список, min_length=1
        }
        with pytest.raises(ValidationError) as exc:
            MealBaseIn(**data)
        assert "components" in str(exc.value)

    def test_meal_base_in_missing_components(self):
        """Тест отсутствия компонентов"""
        data = {
            "name": "завтрак",
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            # components отсутствует
        }
        with pytest.raises(ValidationError) as exc:
            MealBaseIn(**data)
        assert "components" in str(exc.value)

    def test_meal_create_in_inheritance(self):
        """Тест наследования MealCreateIn от MealBaseIn"""
        data = {
            "name": "завтрак",
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            "components": [
                {
                    "name": "Овсянка",
                    "weight": 200,
                    "calories": 350,
                    "protein": 12,
                    "fat": 6,
                    "carbohydrates": 60,
                }
            ],
        }
        meal = MealCreateIn(**data)
        assert meal.name == "завтрак"
        assert isinstance(meal, MealBaseIn)

    def test_meal_update_in_valid(self):
        """Тест валидной схемы обновления"""
        data = {
            "id": uuid.uuid4(),
            "name": "обед",
            "meal_date": datetime.date.today(),
        }
        meal = MealUpdateIn(**data)

        assert meal.name == "обед"
        assert meal.meal_date == datetime.date.today()
        assert meal.meal_time is None
        assert meal.components is None

    def test_meal_update_in_invalid_name(self):
        """Тест невалидного имени в обновлении"""
        data = {
            "id": uuid.uuid4(),
            "name": "полдник",  # не из списка допустимых
        }
        with pytest.raises(ValidationError) as exc:
            MealUpdateIn(**data)
        assert "meal_name must be one of" in str(exc.value)

    def test_meal_update_in_missing_id(self):
        """Тест отсутствия обязательного id"""
        data = {
            "name": "обед",
        }
        with pytest.raises(ValidationError) as exc:
            MealUpdateIn(**data)
        assert "id" in str(exc.value)

    def test_meal_update_in_with_components(self):
        """Тест обновления с компонентами"""
        data = {
            "id": uuid.uuid4(),
            "name": "обед",
            "components": [
                {
                    "name": "Паста",
                    "weight": 250,
                    "calories": 400,
                    "protein": 12,
                    "fat": 8,
                    "carbohydrates": 70,
                }
            ],
        }
        meal = MealUpdateIn(**data)

        assert len(meal.components) == 1
        assert meal.components[0].name == "Паста"

    def test_meal_out_creation(self):
        """Тест создания MealOut"""
        meal_id = uuid.uuid4()
        patient_id = uuid.uuid4()
        dish_id = uuid.uuid4()
        now = datetime.datetime.now()

        data = {
            "id": meal_id,
            "patient_id": patient_id,
            "name": "завтрак",
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            "components": [
                {
                    "id": dish_id,
                    "name": "Овсянка",
                    "weight": 200,
                    "calories": 350,
                    "protein": 12,
                    "fat": 6,
                    "carbohydrates": 60,
                    "created_at": now,
                    "updated_at": now,
                }
            ],
            "created_at": now,
            "updated_at": now,
            "total_weight": 200,
            "total_calories": 350,
            "total_protein": 12,
            "total_fat": 6,
            "total_carbohydrates": 60,
        }
        meal = MealOut(**data)

        assert meal.id == meal_id
        assert meal.patient_id == patient_id
        assert meal.name == "завтрак"
        assert len(meal.components) == 1
        assert meal.total_calories == 350
        assert meal.total_weight == 200

    def test_meal_out_config_from_attributes(self):
        """Тест наличия from_attributes в конфиге"""
        assert hasattr(MealOut, "model_config")
        assert isinstance(MealOut.model_config, dict)
        assert MealOut.model_config.get("from_attributes") is True


class TestResponseSchemas:
    """Тесты для схем ответов"""

    def test_meals_response_with_components(self):
        """Тест MealsResponse с компонентами"""
        meal_id = uuid.uuid4()
        patient_id = uuid.uuid4()
        now = datetime.datetime.now()

        meals_data = {
            "name": "meal",
            "components": [
                {
                    "id": meal_id,
                    "patient_id": patient_id,
                    "name": "завтрак",
                    "meal_date": datetime.date.today(),
                    "meal_time": datetime.time(8, 30),
                    "components": [],
                    "created_at": now,
                    "updated_at": now,
                    "total_weight": 200,
                    "total_calories": 350,
                    "total_protein": 12,
                    "total_fat": 6,
                    "total_carbohydrates": 60,
                }
            ],
        }
        response = MealsResponse(**meals_data)

        assert response.name == "meal"
        assert len(response.components) == 1
        assert response.components[0].name == "завтрак"

    def test_meals_response_without_components(self):
        """Тест MealsResponse без компонентов"""
        data = {
            "name": "meal",
            "components": None,
        }
        response = MealsResponse(**data)

        assert response.name == "meal"
        assert response.components is None

    def test_meal_list_out_creation(self):
        """Тест MealListOut"""
        meal_id = uuid.uuid4()

        data = {
            "id": meal_id,
            "name": "завтрак",
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            "total_calories": 350,
            "components_count": 2,
        }
        meal_list = MealListOut(**data)

        assert meal_list.id == meal_id
        assert meal_list.name == "завтрак"
        assert meal_list.total_calories == 350
        assert meal_list.components_count == 2

    def test_meal_list_out_config_from_attributes(self):
        """Тест наличия from_attributes в конфиге MealListOut"""
        assert hasattr(MealListOut, "model_config")
        assert isinstance(MealListOut.model_config, dict)
        assert MealListOut.model_config.get("from_attributes") is True

    def test_daily_summary_out_creation(self):
        """Тест DailySummaryOut"""
        today = datetime.date.today()

        data = {
            "date": today,
            "total_meals": 3,
            "total_calories": 1200,
            "total_protein": 60.5,
            "total_fat": 40.2,
            "total_carbohydrates": 150.8,
            "by_meal_type": {
                "завтрак": {"count": 1, "calories": 400},
                "обед": {"count": 1, "calories": 500},
                "ужин": {"count": 1, "calories": 300},
            },
        }
        summary = DailySummaryOut(**data)

        assert summary.date == today
        assert summary.total_meals == 3
        assert summary.total_calories == 1200
        assert "завтрак" in summary.by_meal_type
        assert summary.by_meal_type["завтрак"]["calories"] == 400


class TestSchemaEdgeCases:
    """Тесты граничных случаев"""

    def test_dish_base_in_minimum_values(self):
        """Тест минимальных допустимых значений"""
        data = {
            "name": "Минимум",
            "weight": 0,  # минимальный вес
            "calories": 0,  # минимальные калории
            "protein": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0,
        }
        dish = DishBaseIn(**data)
        assert dish.weight == 0
        assert dish.calories == 0

    def test_dish_base_in_maximum_values(self):
        """Тест максимальных допустимых значений"""
        data = {
            "name": "Максимум",
            "weight": 10000,
            "calories": 10000,
            "protein": 100.0,
            "fat": 100.0,
            "carbohydrates": 100.0,
        }
        dish = DishBaseIn(**data)
        assert dish.weight == 10000
        assert dish.calories == 10000

    def test_meal_base_in_name_case_insensitive(self):
        """Тест регистронезависимости имени"""
        data = {
            "name": "ЗАВТРАК",  # верхний регистр
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
            "components": [
                {
                    "name": "Овсянка",
                    "weight": 200,
                    "calories": 350,
                    "protein": 12,
                    "fat": 6,
                    "carbohydrates": 60,
                }
            ],
        }
        meal = MealBaseIn(**data)
        # Валидатор приводит к нижнему регистру
        assert meal.name == "завтрак"  # должно стать нижним регистром
