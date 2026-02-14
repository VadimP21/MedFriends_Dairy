from datetime import date

from django.db.models import QuerySet
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
            created_at=payload.created_at,
        )
        dish_objects = [
            Dish(**dish.model_dump(), meal=meal_model) for dish in payload.components
        ]
        Dish.objects.bulk_create(dish_objects)
        # print("@@@@@@@@@@@@@@@@@@", dish_objects)
        return meal_model

    @staticmethod
    def get_meals_by_date(target_date: date, user) -> QuerySet[Meal, Meal]:
        """
        Фильтрация блюд по конкретной дате (день, месяц, год)
        """
        return Meal.objects.filter(
            user=user, created_at__date=target_date
        ).prefetch_related("components")

    @staticmethod
    def get_history_by_date_and_meal_name(
        target_date: date, target_meal_name: str, user
    ) -> QuerySet[Meal, Meal]:
        return (
            Meal.objects.filter(
                user=user, created_at__date=target_date, name__iexact=target_meal_name
            )
            .prefetch_related("components")
            .order_by("-created_at")
        )

    @staticmethod
    def update_meal(payload: MealUpdate, user) -> Meal:

        meal_for_update_model = get_object_or_404(Meal, id=payload.id, user=user)

        if payload.name is None:
            payload.name = get_meal_name_by_time(timestamp=payload.created_at)

        payload_data = payload.model_dump(exclude_unset=True)
        components_data = payload_data.pop("components", None)

        for field, value in payload_data.items():
            setattr(meal_for_update_model, field, value)

        meal_for_update_model.save()

        if components_data is not None:
            # -------------- ПЕРЕНЕСТИ В dish_update -------------------
            current_dish_ids = []
            for item in components_data:
                dish_id = item.get("id")
                if dish_id:
                    Dish.objects.filter(id=dish_id, meal=meal_for_update_model).update(
                        **item
                    )
                    current_dish_ids.append(dish_id)
                else:
                    new_dish = Dish.objects.create(**item, meal=meal_for_update_model)
                    current_dish_ids.append(new_dish.id)

                Dish.objects.filter(meal=meal_for_update_model).exclude(
                    id__in=current_dish_ids
                ).delete()

            # ----------------------------------------------------------
        return Meal.objects.prefetch_related("components").get(
            id=meal_for_update_model.id
        )

    @staticmethod
    def delete_meal(meal_id: int, user) -> None:

        meal = get_object_or_404(Meal, id=meal_id, user=user)
        meal.delete()

    @staticmethod
    def meal_photo_handler(file_path: str) -> Meal: ...
