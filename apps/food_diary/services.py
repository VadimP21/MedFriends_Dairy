import datetime
from django.db.models import QuerySet
from typing import Optional

from apps.food_diary.models import Meal, Dish
from apps.food_diary.schemas import MealCreateIn, MealUpdateIn
from apps.accounts.models import PatientProfile
from apps.food_diary.utils import get_meal_name_by_time
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404

class MealService:
    """Сервис для работы с приемами пищи"""

    @staticmethod
    def create_meal(
            *,
            patient: PatientProfile,
            payload: MealCreateIn
    ) -> Meal:
        """
        Создать новый прием пищи
        """
        try:
            with transaction.atomic():
                meal = Meal.objects.create(
                    patient=patient,
                    name=payload.name or get_meal_name_by_time(payload.meal_time),
                    meal_date=payload.meal_date,
                    meal_time=payload.meal_time,
                    portion_size=payload.portion_size,
                    description=payload.description
                )

                dishes = [
                    Dish(
                        **dish.model_dump(),
                        meal=meal
                    )
                    for dish in payload.components
                ]
                Dish.objects.bulk_create(dishes)

            return Meal.objects.prefetch_related('components').get(id=meal.id)
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise ValidationError("A meal with these parameters already exists")
            raise


    @staticmethod
    def update_meal(
            *,
            patient: PatientProfile,
            payload: MealUpdateIn
    ) -> Meal:
        """
        Обновить прием пищи
        """
        try:
            meal = get_object_or_404(Meal, id=payload.id, patient=patient)

            with transaction.atomic():
                update_data = payload.model_dump(exclude_unset=True, exclude={'id', 'components'})
                for field, value in update_data.items():
                    setattr(meal, field, value)

                if 'meal_time' in update_data and not payload.name:
                    meal.name = get_meal_name_by_time(meal.meal_time)

                meal.save()

                if payload.components is not None:
                    meal.components.all().delete()

                    dishes = [
                        Dish(**dish.model_dump(), meal=meal)
                        for dish in payload.components
                    ]
                    Dish.objects.bulk_create(dishes)

            return Meal.objects.prefetch_related('components').get(id=meal.id)
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise ValidationError("A meal with these parameters already exists")
            raise

    @staticmethod
    def delete_meal(
            patient: PatientProfile,
            meal_id: str
    ) -> None:
        """
        Удалить прием пищи
        """
        meal = get_object_or_404(Meal, id=meal_id, patient=patient)
        meal.delete()

    @staticmethod
    def get_daily_summary(
            patient: PatientProfile,
            target_date: datetime.date
    ) -> dict:
        """
        Получить сводку за день
        """
        meals = Meal.objects.filter(
            patient=patient,
            meal_date=target_date
        ).prefetch_related('components')

        total_calories = 0
        total_protein = 0.0
        total_fat = 0.0
        total_carbohydrates = 0.0
        by_meal_type = {}

        for meal in meals:
            total_calories += meal.total_calories
            total_protein += meal.total_protein
            total_fat += meal.total_fat
            total_carbohydrates += meal.total_carbohydrates

            if meal.meal_type not in by_meal_type:
                by_meal_type[meal.meal_type] = {
                    'count': 0,
                    'calories': 0,
                    'protein': 0,
                    'fat': 0,
                    'carbohydrates': 0
                }

            by_meal_type[meal.meal_type]['count'] += 1
            by_meal_type[meal.meal_type]['calories'] += meal.total_calories
            by_meal_type[meal.meal_type]['protein'] += meal.total_protein
            by_meal_type[meal.meal_type]['fat'] += meal.total_fat
            by_meal_type[meal.meal_type]['carbohydrates'] += meal.total_carbohydrates

        return {
            'date': target_date,
            'total_meals': meals.count(),
            'total_calories': total_calories,
            'total_protein': round(total_protein, 1),
            'total_fat': round(total_fat, 1),
            'total_carbohydrates': round(total_carbohydrates, 1),
            'by_meal_type': by_meal_type
        }

    @staticmethod
    def get_meals_by_date(
            patient: PatientProfile,
            target_date: Optional[datetime.date] = None,
    ) -> QuerySet[Meal]:
        """
        Получить приемы пищи за период
        """

        return Meal.objects.filter(
            patient=patient,
            meal_date=target_date
        ).prefetch_related('components').order_by('meal_time')


    @staticmethod
    def get_meals_by_date_range(
            patient: PatientProfile,
            from_date: Optional[datetime.date] = None,
            to_date: Optional[datetime.date] = None
    ) -> QuerySet[Meal]:
        """
        Получить приемы пищи за период
        """
        meals = Meal.objects.filter(patient=patient)

        if from_date:
            meals = meals.filter(meal_date__gte=from_date)
        if to_date:
            meals = meals.filter(meal_date__lte=to_date)

        return meals.prefetch_related('components').order_by('-meal_date', '-meal_time')

    @staticmethod
    def get_meal_by_id(
            patient: PatientProfile,
            meal_id: str
    ) -> Meal:
        """
        Получить конкретный прием пищи по ID
        """
        return get_object_or_404(
            Meal.objects.prefetch_related('components'),
            id=meal_id,
            patient=patient
        )

    @staticmethod
    def get_meals_by_date_range_and_type(
            patient,
            from_date: Optional[datetime.date] = None,
            to_date: Optional[datetime.date] = None,
            meal_type: Optional[str] = None
    ):
        """
        Получить приемы пищи за период с фильтрацией по типу
        """
        meals = Meal.objects.filter(patient=patient)

        if from_date:
            meals = meals.filter(meal_date__gte=from_date)
        if to_date:
            meals = meals.filter(meal_date__lte=to_date)
        if meal_type:
            meals = meals.filter(name=meal_type)

        return meals.prefetch_related('components').order_by('-meal_date', '-meal_time')
