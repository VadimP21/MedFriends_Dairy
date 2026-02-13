from datetime import date
from typing import List

from django.shortcuts import get_object_or_404

from core.food_dairy.models import Meal, Dish
from core.food_dairy.schemas.meal_schemas import MealCreate, MealUpdate
from core.food_dairy.utils import get_meal_name_by_time


class MealService:

    @staticmethod
    def create_meal(payload: MealCreate, user) -> Meal:
        if payload.name is None:
            payload.name = get_meal_name_by_time(timestamp=payload.created_at)

        meal_model = Meal.objects.create(
            user=user,
            name=payload.name,
            portion_size=payload.portion_size,
            description=payload.description,
        )
        dish_objects = [
            Dish(**dish.model_dump(), meal=meal_model) for dish in payload.components
        ]
        Dish.objects.bulk_create(dish_objects)
        # print("@@@@@@@@@@@@@@@@@@", dish_objects)
        return meal_model

    @staticmethod
    def get_meals_by_date(target_date: date, user) -> List[Meal]:
        """
        Фильтрация блюд по конкретной дате (день, месяц, год)
        """

        meals_qwery_set = Meal.objects.filter(
            user=user, created_at__date=target_date
        ).prefetch_related("components")
        return meals_qwery_set

    @staticmethod
    def update_meal(payload: MealUpdate, user) -> Meal:

        meal_for_update_model = get_object_or_404(Meal, id=payload.id, user=user)

        payload_data = payload.model_dump(exclude_unset=True)
        components_data = payload_data.pop("components", None)

        for field, value in payload_data.items():
            setattr(meal_for_update_model, field, value)
        meal_for_update_model.save()

        if components_data is not None:
            # -------------- ПЕРЕНЕСТИ В dish_update -------------------
            new_components = []
            for item in components_data:
                # Пытаемся найти по id или создаем новый (зависит от вашей логики)
                dish_id = item.get("id")
                if dish_id:
                    # Обновляем существующий компонент
                    dish = Dish.objects.filter(id=dish_id).update(**item)
                    new_components.append(dish)
                else:
                    # Создаем новый, если id нет
                    new_dish = Dish.objects.create(**item)
                    new_components.append(new_dish)

                # Привязываем обновленный список к Meal

            meal_for_update_model.components.set(new_components)

            # ----------------------------------------------------------

        meal_model = Meal.objects.prefetch_related("components").get(
            id=meal_for_update_model.id
        )

        print("@@@@@@@@@@@@@@@@@@", meal_model)

        return meal_model

    @staticmethod
    def delete_meal(meal_id: int) -> None:

        meal = get_object_or_404(Meal, id=meal_id)
        meal.delete()

    @staticmethod
    def meal_photo_handler(file_path: str) -> Meal: ...
