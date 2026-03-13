import datetime
import logging

from django.db.models import QuerySet
from typing import Optional, List

from ai_agent import food_analysis_service
from apps.food_diary.base import (
    CreateMealSuccessResponse,
    UpdateMealSuccessResponse,
    GetMealSuccessResponse,
    DeleteMealSuccessResponse,
)
from apps.food_diary.models import Meal
from apps.food_diary.schemas import (
    MealCreateIn,
    MealUpdateIn,
    MealsResponse,
)
from apps.accounts.models import PatientProfile
from apps.food_diary.sql_repository import MealRepository
from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)


class MealService:
    """Сервис для работы с приемами пищи"""

    def __init__(self, meal_repository: MealRepository) -> None:
        self.meal_repository = meal_repository

    def create_meal(
        self, patient: PatientProfile, payload: MealCreateIn
    ) -> CreateMealSuccessResponse:
        """
        Создать новый прием пищи

            Args:
                patient: Профиль пациента
                payload: Схема приема пищи для создания
            Returns:
                CreateMealSuccessResponse: Созданный объект

            Raises:
                ValidationError: Если ошибка входных данных
        """
        created_meal = self.meal_repository.create_meal(patient, payload)
        logger.info(f"Meal created: {created_meal.id}")
        response_data = MealsResponse(components=[created_meal])
        return CreateMealSuccessResponse(
            success=True, message="Meal created successfully", data=response_data
        )

    def update_meal(
        self, patient: PatientProfile, payload: MealUpdateIn
    ) -> UpdateMealSuccessResponse:
        """
        Обновить существующий прием пищи

            Args:
                patient: Профиль пациента
                payload: Схема приема пищи для обновления
            Returns:
                UpdateMealSuccessResponse: Обновленный объект

            Raises:
                ValidationError: Если ошибка входных данных
        """

        meal = self.meal_repository.get_meal(patient, str(payload.id))
        updated_meal = self.meal_repository.update_meal(patient, meal, payload)
        logger.info(f"Meal updated: {updated_meal.id}")
        response_data = MealsResponse(components=[updated_meal])
        return UpdateMealSuccessResponse(
            success=True, message="Meal updated successfully", data=response_data
        )

    def delete_meal(
        self, patient: PatientProfile, meal_id: str
    ) -> DeleteMealSuccessResponse:
        """
        Удалить прием пищи
        """
        self.meal_repository.delete_meal(patient, meal_id)
        return DeleteMealSuccessResponse(
            success=True, message="Meal deleted successfully", deleted_id=str(meal_id)
        )

    def get_meals_by_date(
        self,
        patient: PatientProfile,
        target_date: Optional[datetime.date] = None,
    ) -> QuerySet[Meal]:
        """
        Получить приемы пищи за период
        """
        filters = {"patient": patient, "meal_date": target_date}
        return self.meal_repository.meal_queryset(**filters)

    def get_meal_by_id(
        self, patient: PatientProfile, meal_id: str
    ) -> GetMealSuccessResponse:
        """
        Получить конкретный прием пищи по ID
        """
        meal = self.meal_repository.get_meal(patient, meal_id)
        response_data = MealsResponse(components=[meal])
        return GetMealSuccessResponse(success=True, data=response_data)

    def get_meals_by_date_range_and_type(
        self,
        patient,
        from_date: Optional[datetime.date] = None,
        to_date: Optional[datetime.date] = None,
        meal_type: Optional[str] = None,
    ) -> QuerySet[Meal]:
        """
        Получить приемы пищи за период с фильтрацией по типу
        """

        filters = {"patient": patient}
        if from_date:
            filters["meal_date__gte"] = from_date
        if to_date:
            filters["meal_date__lte"] = to_date
        if meal_type:
            filters["name"] = meal_type
        meals = self.meal_repository.meal_queryset(**filters)
        return meals

    @staticmethod
    def get_meal_by_photo(
        patient: PatientProfile,
        images_bytes: List[bytes],
        name: str = None,
        timeout: int = 2,
    ) -> CreateMealSuccessResponse:
        """
        Создать новый прием пищи по фото, используя create_meal

        Args:
            patient: Профиль пациента
            images_bytes: Список изображений в виде байтов
            name: Название приема пищи (опционально)
            timeout: таймаут запроса к AI
        Returns:
            Созданный объект CreateMealSuccessResponse

        Raises:
            ValidationError: Если ошибка анализа фото или создания
        """
        import asyncio
        from asyncio import TimeoutError

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                task = asyncio.wait_for(
                    food_analysis_service.analyze_food_image(images_bytes=images_bytes),
                    timeout=timeout,
                )
                dishes_data = loop.run_until_complete(task)
            except TimeoutError:
                logger.error(f"AI service timeout after {timeout} seconds")
                raise ValidationError(
                    f"Food analysis service not responding. Please try again later"
                )
            except Exception as e:
                logger.error(f"Error during AI analysis: {e}", exc_info=True)
                raise ValidationError(f"Error analyzing photo: {str(e)}")

            finally:
                loop.close()

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

            logger.info(
                f"Meal created from photo: {meal.id} with {len(dishes_data)} dishes"
            )
            response_data = MealsResponse(components=[meal])
            return CreateMealSuccessResponse(
                success=True, message="Meal created successfully", data=response_data
            )

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creating meal from photo: {e}", exc_info=True)
            raise ValidationError(f"Error analyzing photo: {str(e)}")


meal_service = MealService(meal_repository=MealRepository())
