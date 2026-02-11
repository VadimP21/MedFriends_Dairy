import pytest
import json
from django.urls import reverse
from django.test import Client
from pydantic import ValidationError

from core.dish.schemas import DishCreate


@pytest.mark.django_db
class TestDishAPI:

    @pytest.fixture
    def client(self):
        return Client()

    @pytest.fixture
    def valid_data(self):
        return ({
            "name": "Хлеб цельнозерновой тост",
            "weight": 60,
            "calories": 150,
            "protein": 5.00,
            "fat": 2.00,
            "carbohydrates": 25.00,
            "score": 0.9
        })

    @pytest.fixture
    def invalid_data(self):
        return {"name": "Pasta", "weight": "много"}

    # --- УРОВЕНЬ 1: ТЕСТ СХЕМЫ (Unit) ---
    def test_dish_schema_validation(self, valid_data, invalid_data):
        """Проверяем, что Pydantic правильно валидирует данные"""

        dish = DishCreate.model_validate(valid_data)
        assert dish.name == "Хлеб цельнозерновой тост"

        with pytest.raises(ValidationError):
            DishCreate.model_validate(invalid_data)

    # --- УРОВЕНЬ 2: ТЕСТ ДЕКОРАТОРА И VIEW (Integration) ---

    def test_create_dish_success(self, client):
        """Тест успешного POST запроса с валидным JSON"""
        url = reverse('create_dish')  # Имя вашего path в urls.py
        payload = {
            "name": "Хлеб цельнозерновой тост",
            "weight": 60,
            "calories": 150,
            "protein": 5.00,
            "fat": 2.00,
            "carbohydrates": 25.00,
            "score": 0.9
        }

        response = client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_create_dish_invalid_json(self, client):
        """Тест на битый JSON (проверка обработки декоратором)"""
        url = reverse('create_dish')
        bad_payload = '{"name": "Broken", "weight": '  # Недописанный JSON

        response = client.post(
            url,
            data=bad_payload,
            content_type="application/json"
        )

        assert response.status_code == 400
        assert "Invalid JSON format" in response.json()["error"]

    def test_create_dish_wrong_method(self, client):
        """Тест на отправку GET вместо POST"""
        url = reverse('create_dish')

        response = client.get(url)

        assert response.status_code == 405
        assert response.json()["error"] == "Method not allowed"

    def test_create_dish_empty_body(self, client):
        """Тест на пустой запрос"""
        url = reverse('create_dish')

        response = client.post(
            url,
            data="",
            content_type="application/json"
        )

        assert response.status_code == 400
        assert response.json()["error"] == "Request body is empty"
