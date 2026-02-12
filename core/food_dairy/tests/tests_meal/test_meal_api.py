import json
from django.urls import reverse

from core.food_dairy.tests.tests_meal.test_meal_fixtures import TestMealFixture


class TestMealIntegration(TestMealFixture):
    """
    ТЕСТ ДЕКОРАТОРА И VIEW (Integration)

    """

    def test_create_meal_success(self, client, meal_create_data):
        """Тест успешного POST запроса с валидным JSON"""
        url = reverse("food_diary")

        response = client.post(
            url, data=json.dumps(meal_create_data), content_type="application/json"
        )
        response_data = response.json()
        print("!@!@!@!@!@!@!@!@!@", response.json())

        assert response.status_code == 201
        assert response_data["success"] is True
        assert response_data["message"] == "Meal created successfully"
        assert "data" in response_data
        assert response_data["data"]["name"] == meal_create_data["name"]

    # def test_create_dish_invalid_json(self, client, invalid_data):
    #     """Тест на битый JSON (проверка обработки декоратором)"""
    #     url = reverse("dish_create")
    #
    #     response = client.post(url, data=invalid_data, content_type="application/json")
    #     print("!!!!!!!!!!!!!!!!!", response.json())
    #
    #     assert response.status_code == 400
    #
    # def test_create_dish_wrong_method(self, client):
    #     """Тест на отправку GET вместо POST"""
    #     url = reverse("dish_create")
    #
    #     response = client.get(url)
    #
    #     assert response.status_code == 405
    #     assert response.json()["error"] == "Method not allowed"
    #
    # def test_create_dish_empty_body(self, client):
    #     """Тест на пустой запрос"""
    #     url = reverse("dish_create")
    #
    #     response = client.post(url, data="", content_type="application/json")
    #
    #     assert response.status_code == 400
    #     assert response.json()["error"] == "Request body is empty"
