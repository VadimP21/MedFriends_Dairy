from typing import List

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.accounts.models import PatientProfile
from apps.food_diary.models import Meal, Dish
from apps.food_diary.schemas import MealCreateIn, MealUpdateIn, DishCreateIn
from apps.food_diary.utils import get_meal_name_by_time


class MealRepository:

    @staticmethod
    def get_meal(patient: PatientProfile, meal_id: str) -> Meal:
        return get_object_or_404(
            Meal.objects.prefetch_related("components"), id=meal_id, patient=patient
        )

    @staticmethod
    def meal_queryset(**filters) -> QuerySet:
        return (
            Meal.objects.prefetch_related("components")
            .filter(**filters)
            .order_by("-meal_date", "-meal_time")
        )

    @staticmethod
    def _create_dish(meal: Meal, dishes_payload: List[DishCreateIn]) -> None:
        now = timezone.now()
        dishes = [
            Dish(
                **dish.model_dump(),
                meal=meal,
                created_at=now,
                updated_at=now,
            )
            for dish in dishes_payload
        ]
        Dish.objects.bulk_create(dishes)

    @staticmethod
    def create_meal(patient: PatientProfile, payload: MealCreateIn) -> Meal:
        try:
            with transaction.atomic():
                meal = Meal.objects.create(
                    patient=patient,
                    name=payload.name or get_meal_name_by_time(payload.meal_time),
                    meal_date=payload.meal_date,
                    meal_time=payload.meal_time,
                )
                MealRepository._create_dish(meal, payload.components)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise ValidationError("A meal with these parameters already exists")

        return MealRepository.get_meal(patient, meal.id)

    @staticmethod
    def update_meal(patient: PatientProfile, meal: Meal, payload: MealUpdateIn) -> Meal:
        try:
            with transaction.atomic():
                update_data = payload.model_dump(
                    exclude_unset=True, exclude={"id", "components"}
                )
                for field, value in update_data.items():
                    setattr(meal, field, value)

                if "meal_time" in update_data and not payload.name:
                    meal.name = get_meal_name_by_time(meal.meal_time)

                meal.save()

                if payload.components is not None:
                    meal.components.all().delete()
                    MealRepository._create_dish(meal, payload.components)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise ValidationError("A meal with these parameters already exists")

        return MealRepository.get_meal(patient, meal.id)

    @staticmethod
    def delete_meal(patient: PatientProfile, meal_id: str) -> None:
        meal = MealRepository.get_meal(patient, meal_id)
        meal.delete()
