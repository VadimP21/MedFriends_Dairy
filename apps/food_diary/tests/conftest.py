import uuid

import pytest
import datetime
from unittest.mock import Mock

from apps.accounts.models import PatientProfile
from apps.food_diary.models import Meal

# tests/unit/conftest.py (добавьте эти фикстуры)

import pytest
import datetime
import uuid
from django.utils import timezone

from apps.accounts.models import PatientProfile
from apps.food_diary.models import Meal, Dish, MealTimeSlot


@pytest.fixture
def patient(db):
    """Создает реального пациента в тестовой БД"""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.create_user(
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        email="test@example.com",
        password="testpass123",
    )
    patient = PatientProfile.objects.create(
        user=user, personal_info={"first_name": "Test", "last_name": "User"}
    )
    return patient


@pytest.fixture
def meal(patient):
    """Создает реальный прием пищи в тестовой БД"""
    meal = Meal.objects.create(
        patient=patient,
        name="завтрак",
        meal_date=datetime.date.today(),
        meal_time=datetime.time(8, 30),
    )
    # Явно сохраняем в БД (create уже сохраняет, но для надежности)
    meal.save()
    return meal


@pytest.fixture
def dish(meal):
    """Создает реальное блюдо в тестовой БД"""
    return Dish.objects.create(
        meal=meal,
        name="Овсянка",
        weight=200,
        calories=350,
        protein=12.5,
        fat=6.2,
        carbohydrates=60.1,
    )


@pytest.fixture
def meal_time_slot():
    """Создает реальный временной слот в тестовой БД"""
    return MealTimeSlot.objects.create(
        title="завтрак",
        start_hour=6,
        end_hour=10,
    )


@pytest.fixture
def meal_factory():
    """Фабрика для создания приемов пищи"""

    def _create_meal(patient=None, **kwargs):
        if patient is None:
            # Создаем пациента, если не передан
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.create_user(
                username=f"factory_user_{uuid.uuid4().hex[:8]}",
                email="factory@example.com",
                password="testpass123",
            )
            patient = PatientProfile.objects.create(user=user)

        defaults = {
            "name": "завтрак",
            "meal_date": datetime.date.today(),
            "meal_time": datetime.time(8, 30),
        }
        defaults.update(kwargs)

        return Meal.objects.create(patient=patient, **defaults)

    return _create_meal


@pytest.fixture
def dish_factory():
    """Фабрика для создания блюд"""

    def _create_dish(meal=None, **kwargs):
        if meal is None:
            # Создаем прием пищи, если не передан
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.create_user(
                username=f"dish_factory_user_{uuid.uuid4().hex[:8]}",
                email="dish@example.com",
                password="testpass123",
            )
            patient = PatientProfile.objects.create(user=user)
            meal = Meal.objects.create(
                patient=patient,
                name="завтрак",
                meal_date=datetime.date.today(),
                meal_time=datetime.time(8, 30),
            )

        defaults = {
            "name": "Блюдо",
            "weight": 200,
            "calories": 350,
            "protein": 12.5,
            "fat": 6.2,
            "carbohydrates": 60.1,
        }
        defaults.update(kwargs)

        return Dish.objects.create(meal=meal, **defaults)

    return _create_dish


@pytest.fixture
def mock_patient():
    """Мок пациента"""
    patient = Mock(spec=PatientProfile)
    patient.id = uuid.uuid4()
    return patient


@pytest.fixture
def mock_meal():
    """Мок приема пищи"""
    meal = Mock(spec=Meal)
    meal.id = uuid.uuid4()
    meal.name = "завтрак"
    meal.meal_date = datetime.date.today()
    meal.meal_time = datetime.time(8, 0)
    meal.patient_id = "test-patient-id"
    meal._state = Mock()
    meal._state.adding = False
    meal._state.db = None
    meal.save = Mock()
    meal.delete = Mock()
    meal.total_calories = 500
    meal.total_protein = 20
    meal.total_fat = 15
    meal.total_carbohydrates = 65
    meal.components.all.return_value = []
    meal.components = Mock()
    return meal


@pytest.fixture
def mock_meals_queryset(mock_meal):
    """Мок queryset для meals"""
    queryset = Mock()
    queryset.filter.return_value = queryset
    queryset.prefetch_related.return_value = queryset
    queryset.order_by.return_value = queryset
    queryset.return_value = [mock_meal, mock_meal]
    queryset.count.return_value = 2
    return queryset


@pytest.fixture
def mock_dish_queryset():
    """Мок queryset для dishes"""
    queryset = Mock()
    queryset.all.return_value = []
    queryset.delete.return_value = None
    return queryset


@pytest.fixture
def mock_meal_data():
    """Тестовые данные для создания приема пищи"""
    return {
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
            },
            {
                "name": "Банан",
                "weight": 120,
                "calories": 100,
                "protein": 1,
                "fat": 0.3,
                "carbohydrates": 25,
            },
        ],
    }


@pytest.fixture
def mock_update_data():
    """Тестовые данные для обновления"""
    return {
        "id": uuid.uuid4(),
        "name": "обед",
    }


@pytest.fixture
def mock_update_data_with_components():
    """Тестовые данные для обновления с компонентами"""
    return {
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


@pytest.fixture
def mock_dishes_data():
    """Тестовые данные для блюд из фото"""
    return [
        {
            "name": "Паста",
            "weight": 250,
            "calories": 400,
            "protein": 12,
            "fat": 8,
            "carbohydrates": 70,
        },
        {
            "name": "Салат",
            "weight": 150,
            "calories": 120,
            "protein": 3,
            "fat": 5,
            "carbohydrates": 15,
        },
    ]
