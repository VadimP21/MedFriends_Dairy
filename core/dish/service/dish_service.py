from datetime import datetime, date
from typing import List

from core.dish.models import Dish, Meal
from core.dish.schemas.dish_schemas import DishCreate, DishUpdate


class DishService:

    @staticmethod
    def hard_create_dish(payload: DishCreate) -> Dish:
        dish_model = Dish.objects.create(**payload.model_dump())

        return dish_model

    @staticmethod
    def create_dish(payload: DishCreate) -> Dish | None:

        dish_model = Dish(**payload.model_dump())
        if dish_model.checking_correctness_of_calories():
            dish_model = Dish.objects.create(**payload.model_dump())
            return dish_model
        return None

    @staticmethod
    def get_dish_by_id(dish_id: int) -> Dish:
        dish_model = Dish.objects.get(pk=dish_id)
        return dish_model

    @staticmethod
    def get_dish_by_timestamp(timestamp: datetime) -> Dish:
        dish_model = Dish.objects.get(pk=dish_id)
        return dish_model

    @staticmethod
    def get_dishes_by_date(target_date: date) -> List[Dish]:
        """
        Фильтрация блюд по конкретной дате (день, месяц, год)
        """
        return Dish.objects.filter(created_at__date=target_date)

    @staticmethod
    def update_dish(dish_id: int, payload: DishUpdate) -> Dish:

        dish_for_update_model = Dish.objects.get(pk=dish_id)
        dish_for_update_model.objects.update(**payload.model_dump())
        return dish_for_update_model

    @staticmethod
    def delete_dish(dish_id: int) -> None:
        dish_model = Dish.objects.get(pk=dish_id)
        dish_model.delete()
