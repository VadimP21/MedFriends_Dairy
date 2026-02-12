from datetime import date
from typing import List

from core.food_dairy.models import Meal, Dish
from core.food_dairy.schemas.meal_schemas import MealCreate


class MealService:

    @staticmethod
    def create_meal(payload: MealCreate, user) -> Meal:
        # if payload.name is None:
        #     name = utils.install_name_by_time(payload.time)

        meal_model = Meal.objects.create(
            user=user,
            name=payload.name,
            portion_size=payload.portion_size,
            description=payload.description,
        )
        # 2. Создаем связанные блюда
        dish_objects = [
            Dish(**dish.model_dump(), meal=meal_model) for dish in payload.components
        ]
        Dish.objects.bulk_create(dish_objects)
        return meal_model

    @staticmethod
    def get_meals_by_date(target_date: date, user) -> List[Meal]:
        """
        Фильтрация блюд по конкретной дате (день, месяц, год)
        """

        meals_qwery_set = Meal.objects.filter(user=user, created_at__date=target_date).prefetch_related('components')
        meals_model = []
        for meal in meals_qwery_set:
            meals_model.append({
                "id": meal.pk,
                "name": meal.name,
                "portion_size": meal.portion_size,
                "created_at": meal.created_at,
                "components": list(meal.components.values())
            })
        return meals_model