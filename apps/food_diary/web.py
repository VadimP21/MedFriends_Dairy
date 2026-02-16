
from apps.food_diary.base import CreateMealSuccessResponse, ValidationErrorResponse, ErrorResponse, \
    UpdateMealSuccessResponse, NotFoundResponse, GetMealSuccessResponse, DeleteMealSuccessResponse, \
    GetMealsSuccessResponse
from apps.food_diary.models import Meal
from apps.food_diary.schemas import (
    MealCreateIn, MealUpdateIn, MealsResponse
)
from apps.food_diary.services import MealService
from apps.accounts.models import PatientProfile
from apps.food_diary.utils import parse_uuid
from ninja import Router, Query
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from django.db import OperationalError, IntegrityError
import datetime
from typing import Optional


# Хелпер для получения профиля пациента
def _get_patient_profile(request: HttpRequest) -> PatientProfile:
    """
    Получить профиль текущего пациента.
    В тестовом проекте всегда возвращает первого пациента.
    """
    # В реальном проекте здесь была бы проверка авторизации
    # А пока возвращаем тестового пациента
    patient = PatientProfile.objects.first()
    if not patient:
        # Если нет пациентов, создаем тестового
        from apps.accounts.models import User
        user = User.objects.create_user(
            username="test_patient",
            email="patient@test.com",
            password="testpass123"
        )
        patient = PatientProfile.objects.create(
            user=user,
            personal_info={"first_name": "Тест", "last_name": "Пациентов"}
        )
    return patient


# СОЗДАЕМ ЗАЩИЩЕННЫЙ РОУТЕР
food_dairy_routes = Router(tags=["Food"])


# MARK: - Meal CRUD

@food_dairy_routes.post("/", response={
    201: CreateMealSuccessResponse,
    400: ValidationErrorResponse,
    403: ErrorResponse,
    409: ErrorResponse,
    500: ErrorResponse,
})
def create_meal(
        request: HttpRequest,
        payload: MealCreateIn
):
    """
    Создать новый прием пищи

    Returns:
        201: Meal created successfully
        400: Validation error (invalid input data)
        403: Permission denied
        409: Conflict (duplicate entry)
        500: Internal server error
    """
    try:
        patient = _get_patient_profile(request)

        meal = MealService.create_meal(
            patient=patient,
            payload=payload
        )
        response_data = MealsResponse(components=[meal])
        return 201, CreateMealSuccessResponse(
            success=True,
            message="Meal created successfully",
            data=response_data
        )


    except ValidationError as e:
        return 400, ValidationErrorResponse(
            error="Validation error",
            detail=str(e),
            field_errors=getattr(e, 'message_dict', None)
        )
    except PermissionError:
        return 403, ErrorResponse(
            error="Permission denied",
            detail="You don't have permission to create meals"
        )
    except IntegrityError as e:
        if 'unique constraint' in str(e).lower():
            return 409, ErrorResponse(
                error="Conflict",
                detail="A meal with these parameters already exists"
            )
        raise
    except Exception as e:
        # Логируем неожиданные ошибки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in create_meal: {e}", exc_info=True)

        return 500, ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        )


@food_dairy_routes.put("/", response={
    200: UpdateMealSuccessResponse,
    400: ValidationErrorResponse,
    403: ErrorResponse,
    404: NotFoundResponse,
    409: ErrorResponse,
    500: ErrorResponse,
})
def update_meal(
        request: HttpRequest,
        payload: MealUpdateIn
):
    """
    Обновить прием пищи

    Returns:
        200: Meal updated successfully
        400: Validation error (invalid input data)
        403: Permission denied
        404: Meal not found
        409: Conflict (duplicate entry)
        500: Internal server error
    """
    try:
        patient = _get_patient_profile(request)
        if not payload.id:
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail="Meal ID is required for update"
            )
        is_valid, result = parse_uuid(payload.id)
        if not is_valid:
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail=f"Invalid meal ID: {result}"
            )

        payload.id = result

        meal = MealService.update_meal(
            patient=patient,
            payload=payload
        )

        response_data = MealsResponse(components=[meal])

        return 200, UpdateMealSuccessResponse(
            success=True,
            message="Meal updated successfully",
            data=response_data
        )

    except ValidationError as e:
        return 400, ValidationErrorResponse(
            error="Validation error",
            detail=str(e)
        )


@food_dairy_routes.get("/{meal_id}", response={
    200: GetMealSuccessResponse,
    400: ValidationErrorResponse,
    403: ErrorResponse,
    404: NotFoundResponse,
    500: ErrorResponse,
})
def get_meal_by_id(request: HttpRequest, meal_id: str):
    """
    Получить детали конкретного приема пищи по ID

    Поддерживает UUID в форматах:
    - С дефисами: 3fa85f64-5717-4562-b3fc-2c963f66afa6
    - Без дефисов: 3fa85f6457174562b3fc2c963f66afa6

    Returns:
        200: Meal found
        400: Invalid UUID format
        403: Permission denied
        404: Meal not found
        500: Internal server error
    """
    try:
        is_valid, result = parse_uuid(meal_id)
        if not is_valid:
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail=f"Invalid meal ID: {result}"
            )

        patient = _get_patient_profile(request)

        meal = MealService.get_meal_by_id(
            patient=patient,
            meal_id=str(meal_id)
        )

        response_data = MealsResponse(components=[meal])

        return 200, GetMealSuccessResponse(
            success=True,
            data=response_data
        )

    except PermissionError:
        return 403, ErrorResponse(
            error="Permission denied",
            detail="You don't have permission to view this meal"
        )
    except Meal.DoesNotExist:
        return 404, NotFoundResponse(
            error="Not found",
            detail=f"Meal with id {meal_id} not found"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in get_meal_by_id: {e}", exc_info=True)

        return 500, ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        )


@food_dairy_routes.get("/", response={
    200: GetMealsSuccessResponse,
    400: ValidationErrorResponse,
    403: ErrorResponse,
    500: ErrorResponse,
})
def get_meals_by_date(
        request: HttpRequest,
        date_time: Optional[datetime.date] = Query(None, alias="dateTime"),
        from_date: Optional[datetime.date] = Query(None),
        to_date: Optional[datetime.date] = Query(None),
):
    """
    Получить список приемов пищи с фильтрацией

    Параметры фильтрации:
    - dateTime: конкретная дата (YYYY-MM-DD)
    - from_date: начало периода (YYYY-MM-DD)
    - to_date: конец периода (YYYY-MM-DD)

    Примеры:
    - /api/app/v1/foodDairy/?dateTime=2026-02-13
    - /api/app/v1/foodDairy/?from_date=2026-02-01&to_date=2026-02-13

    Returns:
        200: Meals found (может быть пустой список)
        400: Invalid date format
        403: Permission denied
        500: Internal server error
    """
    try:
        patient = _get_patient_profile(request)

        # Если указан dateTime, используем его как единственную дату
        if date_time and not isinstance(date_time, datetime.date):
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail="dateTime must be a valid date in format YYYY-MM-DD"
            )

        if from_date and not isinstance(from_date, datetime.date):
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail="from_date must be a valid date in format YYYY-MM-DD"
            )

        if to_date and not isinstance(to_date, datetime.date):
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail="to_date must be a valid date in format YYYY-MM-DD"
            )
        # Если указан dateTime, используем его как единственную дату

        if date_time:
            meals = MealService.get_meals_by_date_range(
                patient=patient,
                from_date=date_time,
                to_date=date_time
            )
            filters = {"date": str(date_time)}
        else:
            meals = MealService.get_meals_by_date_range(
                patient=patient,
                from_date=from_date,
                to_date=to_date
            )
            filters = {}
            if from_date:
                filters["from"] = str(from_date)
            if to_date:
                filters["to"] = str(to_date)

        meals_list = list(meals)
        response_data = MealsResponse(components=meals_list)

        return 200, GetMealsSuccessResponse(
            success=True,
            data=response_data,
            count=len(meals_list),
            filters=filters if filters else None
        )

    except PermissionError:
        return 403, ErrorResponse(
            error="Permission denied",
            detail="You don't have permission to view meals"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in get_meals: {e}", exc_info=True)

        return 500, ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        )


# В web.py
@food_dairy_routes.delete("/", response={
    200: DeleteMealSuccessResponse,
    400: ValidationErrorResponse,
    403: ErrorResponse,
    404: NotFoundResponse,
    503: ErrorResponse,
    500: ErrorResponse,
})
def delete_meal(
        request: HttpRequest,
        meal_id: str = Query(..., alias="mealId"),
):
    """
        Удалить прием пищи по ID

        Поддерживает UUID в форматах:
        - С дефисами: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        - Без дефисов: 3fa85f6457174562b3fc2c963f66afa6

        Returns:
            200: Meal deleted successfully
            400: Invalid UUID format
            403: Permission denied
            404: Meal not found
            503: Database busy
            500: Internal server error
        """
    # Валидация UUID
    try:
        is_valid, result = parse_uuid(meal_id)
        if not is_valid:
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail=f"Invalid meal ID: {result}"
            )

        patient = _get_patient_profile(request)

        MealService.delete_meal(
            patient=patient,
            meal_id=result
        )
        return 200, DeleteMealSuccessResponse(
            success=True,
            message="Meal deleted successfully",
            deleted_id=result
        )

    except PermissionError:
        return 403, ErrorResponse(
            error="Permission denied",
            detail="You don't have permission to delete this meal"
        )
    except Meal.DoesNotExist:
        return 404, NotFoundResponse(
            error="Not found",
            detail=f"Meal with id {meal_id} not found"
        )
    except OperationalError as e:
        if 'database is locked' in str(e).lower():
            return 503, ErrorResponse(
                error="Database busy",
                detail="The database is currently locked. Please try again."
            )
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in delete_meal: {e}", exc_info=True)

        return 500, ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        )


@food_dairy_routes.get("/history/", response={
    200: GetMealsSuccessResponse,
    400: ValidationErrorResponse,
    403: ErrorResponse,
    500: ErrorResponse,
})
def get_history_by_date_and_meal_name(
        request: HttpRequest,
        date_time: Optional[datetime.date] = Query(None, alias="dateTime"),
        from_date: Optional[datetime.date] = Query(None),
        to_date: Optional[datetime.date] = Query(None),
        meal_type: Optional[str] = Query(alias="mealType"),
):
    """
    Получить историю приемов пищи с фильтрацией по дате и типу приема

    Параметры фильтрации:
    - dateTime: конкретная дата (YYYY-MM-DD) - приоритетнее from_date/to_date
    - from_date: начало периода (YYYY-MM-DD)
    - to_date: конец периода (YYYY-MM-DD)
    - mealType: тип приема пищи (breakfast/lunch/dinner/snack)

    Примеры:
    - /api/app/v1/foodDairy/history/?dateTime=2026-02-13&mealType=breakfast
    - /api/app/v1/foodDairy/history/?from_date=2026-02-01&to_date=2026-02-13&mealType=lunch
    - /api/app/v1/foodDairy/history/?mealType=dinner  (все приемы типа dinner)

    Returns:
        200: Meals found (может быть пустой список)
        400: Invalid date format or meal type
        403: Permission denied
        500: Internal server error
    """
    try:
        patient = _get_patient_profile(request)

        # Валидация meal_type если указан
        valid_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        if meal_type and meal_type not in valid_meal_types:
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail=f"Invalid meal_type. Must be one of: {', '.join(valid_meal_types)}"
            )

        # Если указан dateTime, используем его как единственную дату
        if date_time and not isinstance(date_time, datetime.date):
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail="dateTime must be a valid date in format YYYY-MM-DD"
            )

        if from_date and not isinstance(from_date, datetime.date):
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail="from_date must be a valid date in format YYYY-MM-DD"
            )

        if to_date and not isinstance(to_date, datetime.date):
            return 400, ValidationErrorResponse(
                error="Validation error",
                detail="to_date must be a valid date in format YYYY-MM-DD"
            )
        # Определяем диапазон дат
        if date_time:
            from_date = date_time
            to_date = date_time

        # Получаем meals с фильтрацией по дате и типу
        meals = MealService.get_meals_by_date_range_and_type(
            patient=patient,
            from_date=from_date,
            to_date=to_date,
            meal_type=meal_type
        )

        # Формируем фильтры для ответа
        filters = {}
        if date_time:
            filters["date"] = str(date_time)
        else:
            if from_date:
                filters["from"] = str(from_date)
            if to_date:
                filters["to"] = str(to_date)
        if meal_type:
            filters["meal_type"] = meal_type

        meals_list = list(meals)
        response_data = MealsResponse(components=meals_list)

        return 200, GetMealsSuccessResponse(
            success=True,
            data=response_data,
            count=len(meals_list),
            filters=filters if filters else None
        )

    except PermissionError:
        return 403, ErrorResponse(
            error="Permission denied",
            detail="You don't have permission to view meals"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in get_history: {e}", exc_info=True)

        return 500, ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        )
