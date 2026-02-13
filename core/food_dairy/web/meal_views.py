"""
like web.py in Base project
"""

from datetime import datetime
from typing import List

from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pydantic import TypeAdapter

from core.food_dairy.service.meal_service import MealService
from core.food_dairy.schemas.dish_schemas import DishCreate, DishResponse, DishUpdate
from core.food_dairy.schemas.meal_schemas import (
    MealCreate,
    MealResponse,
    AllMealsResponse,
)
from core.food_dairy.utils import (
    validate_json_request,
    validate_json_body,
    is_dat_is_valid,
)


@csrf_exempt
@validate_json_body
@require_http_methods(["GET"])
def get_by_photo(): ...


@csrf_exempt
@validate_json_body
@require_http_methods(["GET"])
def get_by_voice(): ...


@csrf_exempt
@validate_json_body
@require_http_methods(["GET"])
def get_by_id(): ...


@csrf_exempt
@validate_json_body
@require_http_methods(["POST", "GET", "PUT", "DELETE"])
def food_diary_view(request: HttpRequest):
    # user = request.user.id
    # ---------- DEVELOPING -------------
    user = User.objects.get(id=1)
    # ---------- DEVELOPING -------------
    if request.method == "POST":
        try:
            meal = MealCreate.model_validate(request.json_data)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

        with transaction.atomic():
            meal_model = MealService.create_meal(payload=meal, user=user)
            meal_response = MealResponse.model_validate(meal_model)
            response = AllMealsResponse(name="meal", components=[meal_response])
        return JsonResponse(
            {
                "success": True,
                "data": response.model_dump(),
                "message": "Meal created successfully",
            },
            status=201,
        )

    elif request.method == "GET":
        date_str = request.GET.get("dateTime")
        if not date_str:
            return JsonResponse(
                {"success": False, "error": "dateTime parameter is required"},
                status=400,
            )

        try:
            target_date = is_dat_is_valid(date_str=date_str)

        except ValueError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid date format. Please use DD.MM.YYYY (e.g. 10.02.2026)",
                },
                status=400,
            )

        meals_model = MealService.get_meals_by_date(target_date=target_date, user=user)

        adapter = TypeAdapter(List[MealResponse])
        meals = adapter.validate_python(meals_model)

        response = AllMealsResponse(name="meal", components=meals)
        return JsonResponse(
            {
                "success": True,
                "data": response.model_dump(),
                "message": "Meal created successfully",
            },
            status=200,
        )
