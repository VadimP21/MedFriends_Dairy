import datetime

from django.db.models import QuerySet
from typing import Optional, List

from ai_agent import food_analysis_service
from apps.food_diary.models import Meal, Dish
from apps.food_diary.schemas import MealCreateIn, MealUpdateIn, DishCreateIn
from apps.accounts.models import PatientProfile
from apps.food_diary.utils import get_meal_name_by_time
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone


class MealService:
    """Сервис для работы с приемами пищи"""

    @staticmethod
    def create_meal(*, patient: PatientProfile, payload: MealCreateIn) -> Meal:
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
                )
                now = timezone.now()
                dishes = [
                    Dish(
                        **dish.model_dump(),
                        meal=meal,
                        created_at=now,
                        updated_at=now,
                    )
                    for dish in payload.components
                ]
                Dish.objects.bulk_create(dishes)

            return Meal.objects.prefetch_related("components").get(id=meal.id)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise ValidationError("A meal with these parameters already exists")
            raise

    @staticmethod
    def update_meal(*, patient: PatientProfile, payload: MealUpdateIn) -> Meal:
        """
        Обновить прием пищи
        """
        try:
            meal = get_object_or_404(Meal, id=payload.id, patient=patient)

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

                    dishes = [
                        Dish(**dish.model_dump(), meal=meal)
                        for dish in payload.components
                    ]
                    Dish.objects.bulk_create(dishes)

            return Meal.objects.prefetch_related("components").get(id=meal.id)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise ValidationError("A meal with these parameters already exists")
            raise

    @staticmethod
    def delete_meal(patient: PatientProfile, meal_id: str) -> None:
        """
        Удалить прием пищи
        """
        meal = get_object_or_404(Meal, id=meal_id, patient=patient)
        meal.delete()

    @staticmethod
    def get_meals_by_date(
        patient: PatientProfile,
        target_date: Optional[datetime.date] = None,
    ) -> QuerySet[Meal]:
        """
        Получить приемы пищи за период
        """

        return (
            Meal.objects.filter(patient=patient, meal_date=target_date)
            .prefetch_related("components")
            .order_by("meal_time")
        )

    @staticmethod
    def get_meals_by_date_range(
        patient: PatientProfile,
        from_date: Optional[datetime.date] = None,
        to_date: Optional[datetime.date] = None,
    ) -> QuerySet[Meal]:
        """
        Получить приемы пищи за период
        """
        meals = Meal.objects.filter(patient=patient)

        if from_date:
            meals = meals.filter(meal_date__gte=from_date)
        if to_date:
            meals = meals.filter(meal_date__lte=to_date)

        return meals.prefetch_related("components").order_by("-meal_date", "-meal_time")

    @staticmethod
    def get_meal_by_id(patient: PatientProfile, meal_id: str) -> Meal:
        """
        Получить конкретный прием пищи по ID
        """
        return get_object_or_404(
            Meal.objects.prefetch_related("components"), id=meal_id, patient=patient
        )

    @staticmethod
    def get_meals_by_date_range_and_type(
        patient,
        from_date: Optional[datetime.date] = None,
        to_date: Optional[datetime.date] = None,
        meal_type: Optional[str] = None,
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

        return meals.prefetch_related("components").order_by("-meal_date", "-meal_time")

    @staticmethod
    async def get_meal_by_photo(
        patient: PatientProfile, image_bytes: bytes, name: str = None
    ) -> Meal:
        """
        Создать новый прием пищи по фото, используя create_meal

        Args:
            patient: Профиль пациента
            image_bytes: Байты изображения
            name: Название приема пищи (опционально)

        Returns:
            Созданный объект Meal

        Raises:
            ValidationError: Если ошибка анализа фото или создания
        """
        try:
            # 1. Анализируем фото через AI сервис
            dishes_data: List[DishCreateIn] = (
                await food_analysis_service.analyze_food_image(
                    image=image_bytes,
                )
            )

            if not dishes_data:
                raise ValidationError("No dishes detected in the photo")

            now = timezone.now()
            meal_payload = MealCreateIn(
                name=name,
                meal_date=now.date(),
                meal_time=now.time(),
                components=dishes_data,
            )

            meal = MealService.create_meal(patient=patient, payload=meal_payload)
            import logging

            logger = logging.getLogger(__name__)

            logger.info(
                f"Meal created from photo: {meal.id} with {len(dishes_data)} dishes"
            )
            return meal

        except ValidationError:
            raise
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error creating meal from photo: {e}", exc_info=True)
            raise ValidationError(f"Error analyzing photo: {str(e)}")
