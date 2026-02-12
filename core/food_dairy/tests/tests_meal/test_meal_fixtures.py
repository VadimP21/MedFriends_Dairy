import pytest
from django.test import Client


@pytest.mark.django_db
class TestMealFixture:

    @pytest.fixture
    def client(self):
        return Client()

    @pytest.fixture
    def user(self):
        return 1

    @pytest.fixture
    def meal_create_data(self):
        return {
            "name": "Завтрак",
            "components": [
                {
                    "name": "Хлеб цельнозерновой тост",
                    "weight": 60,
                    "calories": 150,
                    "protein": 5.00,
                    "fat": 2.00,
                    "carbohydrates": 25.00,
                    "score": 0.9,
                },
                {
                    "name": "Яйцо жареное (2 шт)",
                    "weight": 100,
                    "calories": 190,
                    "protein": 13.00,
                    "fat": 14.00,
                    "carbohydrates": 1.00,
                    "score": 0.95,
                },
                {
                    "name": "Авокадо",
                    "weight": 80,
                    "calories": 160,
                    "protein": 2.00,
                    "fat": 15.00,
                    "carbohydrates": 9.00,
                    "score": 0.9,
                },
                {
                    "name": "Помидоры черри",
                    "weight": 30,
                    "calories": 10,
                    "protein": 0.60,
                    "fat": 0.10,
                    "carbohydrates": 2.20,
                    "score": 0.85,
                },
                {
                    "name": "Микрозелень",
                    "weight": 10,
                    "calories": 5,
                    "protein": 0.50,
                    "fat": 0.10,
                    "carbohydrates": 1.00,
                    "score": 0.7,
                },
            ],
            "total_weight": 280,
            "total_calories": 515,
            "total_protein": 21.10,
            "total_fat": 31.20,
            "total_carbohydrates": 38.20,
            "portion_size": "Стандартная",
            "score": 0.9,
        }

    @pytest.fixture
    def invalid_data(self):
        return {"name": "Pasta", "weight": "много"}
