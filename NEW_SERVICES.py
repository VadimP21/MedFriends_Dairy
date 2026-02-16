# apps/food_diary/services.py
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404


class MealService:
    @staticmethod
    def create_meal(*, patient, payload):
        """Создать прием пищи с валидацией"""
        try:
            with transaction.atomic():
                # Проверяем права
                if not hasattr(patient, 'can_create_meal') or patient.can_create_meal:
                    # Создаем meal
                    meal = Meal.objects.create(
                        patient=patient,
                        meal_type=payload.meal_type,
                        meal_date=payload.meal_date,
                        meal_time=payload.meal_time,
                        name=payload.name or get_meal_name_by_time(payload.meal_time),
                        portion_size=payload.portion_size,
                        description=payload.description
                    )

                    # Создаем dishes
                    dishes = [
                        Dish(**dish.model_dump(), meal=meal)
                        for dish in payload.components
                    ]
                    Dish.objects.bulk_create(dishes)

                    return Meal.objects.prefetch_related('components').get(id=meal.id)
                else:
                    raise PermissionError("User cannot create meals")

        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise ValidationError("A meal with these parameters already exists")
            raise

    @staticmethod
    def update_meal(*, patient, payload):
        """Обновить прием пищи"""
        try:
            meal = get_object_or_404(Meal, id=payload.id, patient=patient)

            # Проверяем права
            if not hasattr(patient, 'can_edit_meal') or patient.can_edit_meal:
                with transaction.atomic():
                    # Обновляем поля
                    update_data = payload.model_dump(exclude_unset=True, exclude={'id', 'components'})
                    for field, value in update_data.items():
                        setattr(meal, field, value)

                    if 'meal_time' in update_data and not payload.name:
                        meal.name = get_meal_name_by_time(meal.meal_time)

                    meal.save()

                    # Обновляем компоненты
                    if payload.components is not None:
                        meal.components.all().delete()
                        dishes = [
                            Dish(**dish.model_dump(), meal=meal)
                            for dish in payload.components
                        ]
                        Dish.objects.bulk_create(dishes)

                    return Meal.objects.prefetch_related('components').get(id=meal.id)
            else:
                raise PermissionError("User cannot edit this meal")

        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise ValidationError("A meal with these parameters already exists")
            raise

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
            meals = meals.filter(meal_type=meal_type)

        return meals.prefetch_related('components').order_by('-meal_date', '-meal_time')

    # Остальные методы...
