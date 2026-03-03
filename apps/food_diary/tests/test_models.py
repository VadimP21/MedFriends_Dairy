# tests/unit/test_models.py

import pytest
import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.food_diary.models import Dish, Meal, MealTimeSlot


@pytest.mark.django_db
class TestDishModel:
    """Тесты для модели Dish"""

    def test_create_dish(self, meal):
        """Тест создания блюда с реальными объектами"""
        dish = Dish.objects.create(
            meal=meal,
            name="Тестовое блюдо",
            weight=250,
            calories=350,
            protein=15.5,
            fat=8.2,
            carbohydrates=45.3,
        )

        assert dish.id is not None
        assert dish.name == "Тестовое блюдо"
        assert dish.weight == 250
        assert dish.calories == 350
        assert dish.protein == 15.5
        assert dish.fat == 8.2
        assert dish.carbohydrates == 45.3
        assert dish.meal_id == meal.id
        assert dish.created_at is not None
        assert dish.updated_at is not None

    def test_dish_str_method(self, dish):
        """Тест строкового представления"""
        expected = f"{dish.name} ({dish.weight}g)"
        assert str(dish) == expected

    def test_dish_required_fields(self, meal):
        """Тест обязательных полей"""
        with pytest.raises(IntegrityError):
            Dish.objects.create(
                meal=meal,
                # пропущены обязательные поля
            )

    def test_dish_negative_weight(self, meal):
        """Тест отрицательного веса"""
        with pytest.raises(Exception):
            dish = Dish(
                meal=meal,
                name="Тестовое блюдо",
                weight=-100,
                calories=350,
                protein=15.5,
                fat=8.2,
                carbohydrates=45.3,
            )
            dish.full_clean()


@pytest.mark.django_db
class TestMealModel:
    """Тесты для модели Meal"""

    def test_create_meal(self, patient):
        """Тест создания приема пищи"""
        meal_date = datetime.date.today()
        meal_time = datetime.time(8, 30)

        meal = Meal.objects.create(
            patient=patient,
            name="завтрак",
            meal_date=meal_date,
            meal_time=meal_time,
        )

        assert meal.id is not None
        assert meal.patient_id == patient.id
        assert meal.name == "завтрак"
        assert meal.meal_date == meal_date
        assert meal.meal_time == meal_time

    def test_meal_str_method(self, meal):
        """Тест строкового представления"""
        expected = f"{meal.get_name_display()} - {meal.meal_date}"
        assert str(meal) == expected

    def test_meal_name_choices(self, patient):
        """Тест допустимых значений name"""
        valid_names = ["завтрак", "обед", "ужин", "перекус"]

        for name in valid_names:
            meal = Meal.objects.create(
                patient=patient,
                name=name,
                meal_date=datetime.date.today(),
                meal_time=datetime.time(12, 0),
            )
            assert meal.name == name

    def test_meal_invalid_name_choice(self, patient):
        """Тест недопустимого значения name"""
        with pytest.raises(ValidationError):
            meal = Meal(
                patient=patient,
                name="полдник",
                meal_date=datetime.date.today(),
                meal_time=datetime.time(12, 0),
            )
            meal.full_clean()

    def test_meal_total_weight_property(self, meal):
        """Тест свойства total_weight"""
        Dish.objects.create(
            meal=meal,
            name="Блюдо 1",
            weight=200,
            calories=350,
            protein=10,
            fat=5,
            carbohydrates=20,
        )
        Dish.objects.create(
            meal=meal,
            name="Блюдо 2",
            weight=150,
            calories=250,
            protein=8,
            fat=4,
            carbohydrates=15,
        )

        meal.refresh_from_db()
        assert meal.total_weight == 350

    def test_meal_total_calories_property(self, meal):
        """Тест свойства total_calories"""
        Dish.objects.create(
            meal=meal,
            name="Блюдо 1",
            weight=200,
            calories=350,
            protein=10,
            fat=5,
            carbohydrates=20,
        )
        Dish.objects.create(
            meal=meal,
            name="Блюдо 2",
            weight=150,
            calories=250,
            protein=8,
            fat=4,
            carbohydrates=15,
        )

        meal.refresh_from_db()
        assert meal.total_calories == 600

    def test_meal_ordering(self, patient):
        """Тест сортировки"""
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        meal1 = Meal.objects.create(
            patient=patient,
            name="завтрак",
            meal_date=yesterday,
            meal_time=datetime.time(8, 0),
        )
        meal2 = Meal.objects.create(
            patient=patient,
            name="обед",
            meal_date=today,
            meal_time=datetime.time(13, 0),
        )

        meals = Meal.objects.filter(patient=patient)
        assert meals[0] == meal2  # сегодня первым


@pytest.mark.django_db
class TestMealTimeSlotModel:
    """Тесты для модели MealTimeSlot"""

    def test_create_meal_time_slot(self):
        """Тест создания временного слота"""
        slot = MealTimeSlot.objects.create(
            title="завтрак",
            start_hour=6,
            end_hour=10,
        )

        assert slot.id is not None
        assert slot.title == "завтрак"
        assert slot.start_hour == 6
        assert slot.end_hour == 10

    def test_meal_time_slot_str_method(self, meal_time_slot):
        """Тест строкового представления"""
        expected = f"{meal_time_slot.get_title_display()}: {meal_time_slot.start_hour}:00 - {meal_time_slot.end_hour}:00"
        assert str(meal_time_slot) == expected

    def test_meal_time_slot_unique_title(self):
        """Тест уникальности title"""
        MealTimeSlot.objects.create(title="завтрак", start_hour=6, end_hour=10)

        with pytest.raises(IntegrityError):
            MealTimeSlot.objects.create(title="завтрак", start_hour=7, end_hour=11)


@pytest.mark.django_db
class TestModelRelations:
    """Тесты связей"""

    def test_meal_dish_relation(self, meal):
        """Тест связи между Meal и Dish"""
        dish1 = Dish.objects.create(
            meal=meal,
            name="Блюдо 1",
            weight=200,
            calories=350,
            protein=10,
            fat=5,
            carbohydrates=20,
        )
        dish2 = Dish.objects.create(
            meal=meal,
            name="Блюдо 2",
            weight=150,
            calories=250,
            protein=8,
            fat=4,
            carbohydrates=15,
        )
        assert dish1.meal_id == meal.id
        assert dish2.meal_id == meal.id
        assert meal.components.count() == 2
        assert list(meal.components.all()) == [dish1, dish2]

    def test_cascade_delete_meal(self, meal):
        """Тест каскадного удаления - при удалении Meal должны удалиться связанные Dish"""
        # Создаем блюда
        dish1 = Dish.objects.create(
            meal=meal,
            name="Блюдо 1",
            weight=200,
            calories=350,
            protein=10,
            fat=5,
            carbohydrates=20,
        )
        dish2 = Dish.objects.create(
            meal=meal,
            name="Блюдо 2",
            weight=150,
            calories=250,
            protein=8,
            fat=4,
            carbohydrates=15,
        )

        assert Dish.objects.filter(meal=meal).count() == 2
        assert meal.components.count() == 2
        meal_id = meal.id
        dish1_id = dish1.id
        dish2_id = dish2.id
        meal.delete()
        with pytest.raises(Meal.DoesNotExist):
            Meal.objects.get(id=meal_id)

        assert Dish.objects.filter(id=dish1_id).count() == 0
        assert Dish.objects.filter(id=dish2_id).count() == 0
        assert Dish.objects.filter(meal_id=meal_id).count() == 0
