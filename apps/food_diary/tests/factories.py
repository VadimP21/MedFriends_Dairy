# apps/food/tests/factories.py
import factory
import uuid
import datetime
from django.utils import timezone
from factory.django import DjangoModelFactory
from apps.accounts.models import User, PatientProfile
from apps.food_diary.models import Meal, Dish, MealTimeSlot


class UserFactory(DjangoModelFactory):
    """Фабрика для создания пользователей"""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_patient = True


class PatientProfileFactory(DjangoModelFactory):
    """Фабрика для создания профилей пациентов"""

    class Meta:
        model = PatientProfile

    user = factory.SubFactory(UserFactory)
    birth_date = datetime.date(1990, 1, 1)
    height = 175.0
    weight = 70.0
    personal_info = {
        "first_name": "Тест",
        "last_name": "Пациентов",
        "gender": "male"
    }


class MealTimeSlotFactory(DjangoModelFactory):
    """Фабрика для создания временных слотов"""

    class Meta:
        model = MealTimeSlot

    title = factory.Iterator(['breakfast', 'lunch', 'dinner', 'snack'])
    start_hour = factory.Iterator([6, 11, 16, 0])
    end_hour = factory.Iterator([11, 16, 22, 24])


class DishFactory(DjangoModelFactory):
    """Фабрика для создания блюд"""

    class Meta:
        model = Dish

    name = factory.Sequence(lambda n: f"Блюдо {n}")
    weight = factory.Faker('random_int', min=50, max=500)
    calories = factory.Faker('random_int', min=100, max=800)
    protein = factory.Faker('random_int', min=5, max=30)
    fat = factory.Faker('random_int', min=5, max=30)
    carbohydrates = factory.Faker('random_int', min=5, max=30)
    score = factory.Faker('random_int', min=50, max=100) / 100
    description = factory.Faker('sentence')


class MealFactory(DjangoModelFactory):
    """Фабрика для создания приемов пищи"""

    class Meta:
        model = Meal

    patient = factory.SubFactory(PatientProfileFactory)
    name = factory.Iterator(['breakfast', 'lunch', 'dinner', 'snack'])
    meal_date = factory.LazyFunction(datetime.date.today)
    meal_time = factory.LazyFunction(
        lambda: datetime.time(
            hour=factory.Faker('random_int', min=8, max=20).evaluate(None, None, {}),
            minute=factory.Faker('random_int', min=0, max=59).evaluate(None, None, {})
        )
    )
    portion_size = "Стандартная"
    description = factory.Faker('sentence')

    @factory.post_generation
    def with_dishes(self, create, extracted, **kwargs):
        """Добавить блюда к приему пищи"""
        if not create:
            return

        if extracted is None:
            extracted = 2  # по умолчанию 2 блюда

        for i in range(extracted):
            DishFactory(meal=self)