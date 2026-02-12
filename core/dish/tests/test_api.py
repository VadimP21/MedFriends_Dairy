import json
from django.urls import reverse

from core.dish.tests.fixtures import TestDishFixture


class TestDishIntegration(TestDishFixture):
    """
    ТЕСТ ДЕКОРАТОРА И VIEW (Integration)

    """

    def test_create_dish_success(self, client, dish_create_data):
        """Тест успешного POST запроса с валидным JSON"""
        url = reverse("dish_create")

        response = client.post(
            url, data=json.dumps(dish_create_data), content_type="application/json"
        )
        response_data = response.json()
        assert response.status_code == 201
        assert response_data["success"] is True
        assert response_data["message"] == "Dish created successfully"
        assert "data" in response_data
        assert response_data["data"]["name"] == dish_create_data["name"]

    def test_create_dish_invalid_json(self, client, invalid_data):
        """Тест на битый JSON (проверка обработки декоратором)"""
        url = reverse("dish_create")

        response = client.post(url, data=invalid_data, content_type="application/json")
        print("!!!!!!!!!!!!!!!!!", response.json())

        assert response.status_code == 400

    def test_create_dish_wrong_method(self, client):
        """Тест на отправку GET вместо POST"""
        url = reverse("dish_create")

        response = client.get(url)

        assert response.status_code == 405
        assert response.json()["error"] == "Method not allowed"

    def test_create_dish_empty_body(self, client):
        """Тест на пустой запрос"""
        url = reverse("dish_create")

        response = client.post(url, data="", content_type="application/json")

        assert response.status_code == 400
        assert response.json()["error"] == "Request body is empty"
