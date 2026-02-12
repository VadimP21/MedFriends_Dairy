import pytest
from django.test import Client


@pytest.mark.django_db
class TestDishFixture:

    @pytest.fixture
    def client(self):
        return Client()

    @pytest.fixture
    def dish_create_data(self):
        return {
            "name": "Хлеб цельнозерновой тост",
            "weight": 60,
            "calories": 150,
            "protein": 5.00,
            "fat": 2.00,
            "carbohydrates": 25.00,
            "score": 0.9,
        }

    @pytest.fixture
    def invalid_data(self):
        return {"name": "Pasta", "weight": "много"}

    @pytest.fixture
    def url_name(self):
        urls_name = {
            "dish_create": "dish_create",
            "update_dish": "update_dish",
            "read_dish": "read_dish",
            "delete_dish": "delete_dish",
        }
        return urls_name
