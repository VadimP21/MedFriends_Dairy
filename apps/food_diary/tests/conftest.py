import datetime

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from typing import Dict, Any

from apps.food_diary.models import MealTimeSlot
from apps.food_diary.tests.factories import (
    UserFactory, PatientProfileFactory,
    MealFactory, DishFactory, MealTimeSlotFactory
)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Автоматически давать доступ к БД всем тестам"""
    pass


@pytest.fixture
def api_client():
    """Клиент для тестирования API"""
    return APIClient()


@pytest.fixture
def user():
    """Создать обычного пользователя"""
    return UserFactory()


@pytest.fixture
def patient():
    """Создать пациента с профилем"""
    patient_profile = PatientProfileFactory()
    return patient_profile


@pytest.fixture
def patient_user(patient):
    """Вернуть пользователя пациента"""
    return patient.user


@pytest.fixture
def auth_client(patient_user):
    """Клиент с авторизацией"""
    client = APIClient()
    client.force_authenticate(user=patient_user)
    return client


@pytest.fixture
def meal_time_slots():
    """Создать временные слоты"""
    MealTimeSlotFactory(title='breakfast', start_hour=6, end_hour=11)
    MealTimeSlotFactory(title='lunch', start_hour=11, end_hour=16)
    MealTimeSlotFactory(title='dinner', start_hour=16, end_hour=22)
    MealTimeSlotFactory(title='snack', start_hour=0, end_hour=24)
    return MealTimeSlot.objects.all()


@pytest.fixture
def meal(patient):
    """Создать один прием пищи"""
    return MealFactory(patient=patient, with_dishes=2)


@pytest.fixture
def meals(patient):
    """Создать несколько приемов пищи"""
    meals = []
    for i in range(5):
        days_ago = i
        meal_date = datetime.date.today() - datetime.timedelta(days=days_ago)
        meal = MealFactory(
            patient=patient,
            meal_date=meal_date,
            with_dishes=2
        )
        meals.append(meal)
    return meals


@pytest.fixture
def meal_data():
    """Данные для создания приема пищи"""
    return {
        "name": "breakfast",
        "meal_date": str(datetime.date.today()),
        "meal_time": "08:30:00",
        "portion_size": "Стандартная",
        "description": "Тестовый завтрак",
        "components": [
            {
                "name": "Омлет",
                "weight": 200,
                "calories": 350,
                "protein": 20,
                "fat": 25,
                "carbohydrates": 5,
                "score": 0.8,
                "description": "Омлет из 3 яиц"
            },
            {
                "name": "Тост",
                "weight": 50,
                "calories": 150,
                "protein": 5,
                "fat": 5,
                "carbohydrates": 20,
                "score": 0.7,
                "description": "Тост с маслом"
            }
        ]
    }