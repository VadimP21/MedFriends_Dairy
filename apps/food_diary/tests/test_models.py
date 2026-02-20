import pytest
import datetime
from decimal import Decimal

from apps.food_diary.models import Meal, Dish, MealTimeSlot


@pytest.mark.django_db
class TestMealModel:
    """Тесты для модели Meal"""

    def test_create_meal(self, patient):
        """Тест создания приема пищи"""
        meal = Meal.objects.create(
            patient=patient,
            name='breakfast',
            meal_date=datetime.date.today(),
            meal_time=datetime.time(8, 30),
            portion_size='Стандартная'
        )

        assert meal.id is not None
        assert str(meal) == f"Завтрак - {datetime.date.today()}"
        assert meal.patient == patient

    def test_meal_properties(self, meal):
        """Тест вычисляемых свойств"""
        # Создаем блюда
        Dish.objects.create(
            meal=meal,
            name='Омлет',
            weight=200,
            calories=350,
            protein=20,
            fat=25,
            carbohydrates=5,
            score=0.8
        )

        Dish.objects.create(
            meal=meal,
            name='Тост',
            weight=50,
            calories=150,
            protein=5,
            fat=5,
            carbohydrates=20,
            score=0.7
        )

        # Обновляем meal из БД
        meal.refresh_from_db()

        assert meal.total_weight == 250
        assert meal.total_calories == 500
        assert meal.total_protein == 25
        assert meal.total_fat == 30
        assert meal.total_carbohydrates == 25
        assert round(meal.avg_score, 1) == 0.8

    def test_meal_ordering(self, patient):
        """Тест сортировки приемов пищи"""
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        meal1 = Meal.objects.create(
            patient=patient,
            name='breakfast',
            meal_date=today,
            meal_time=datetime.time(9, 0),
            portion_size='Стандартная'
        )

        meal2 = Meal.objects.create(
            patient=patient,
            name='lunch',
            meal_date=yesterday,
            meal_time=datetime.time(13, 0),
            portion_size='Стандартная'
        )

        meals = Meal.objects.filter(patient=patient)
        assert meals[0] == meal1  # Сначала сегодняшний
        assert meals[1] == meal2  # Потом вчерашний


@pytest.mark.django_db
class TestDishModel:
    """Тесты для модели Dish"""

    def test_create_dish(self, meal):
        """Тест создания блюда"""
        dish = Dish.objects.create(
            meal=meal,
            name='Омлет',
            weight=200,
            calories=350,
            protein=20,
            fat=25,
            carbohydrates=5,
            score=0.8
        )

        assert dish.id is not None
        assert str(dish) == "Омлет (200g)"
        assert dish.meal == meal

    def test_checking_correctness_of_calories(self):
        """Тест проверки корректности калорий"""
        # Корректные калории (примерно)
        dish1 = Dish(
            protein=20,  # 20*4 = 80
            carbohydrates=5,  # 5*4 = 20
            fat=25,  # 25*9 = 225
            calories=300  # 80+20+225 = 325 (ошибка 25/300=8.3% < 30%)
        )
        assert dish1.checking_correctness_of_calories() is True

        # Некорректные калории
        dish2 = Dish(
            protein=20,
            carbohydrates=5,
            fat=25,
            calories=500  # Должно быть ~325, ошибка 175/500=35% > 30%
        )
        assert dish2.checking_correctness_of_calories() is False


@pytest.mark.django_db
class TestMealTimeSlotModel:
    """Тесты для модели MealTimeSlot"""

    def test_create_slot(self):
        """Тест создания временного слота"""
        slot = MealTimeSlot.objects.create(
            title='breakfast',
            start_hour=6,
            end_hour=11
        )

        assert slot.id is not None
        assert str(slot) == "Завтрак: 6:00 - 11:00"
        assert slot.get_title_display() == "Завтрак"