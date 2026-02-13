"""
like web.py in Base project
"""

import os
from datetime import datetime
from typing import List

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
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
    MealUpdate,
)
from core.food_dairy.utils import (
    validate_json_request,
    validate_json_body,
    is_dat_is_valid,
)


@csrf_exempt
@validate_json_body
@require_http_methods(["POST"])
def get_by_photo(request: HttpRequest):
    # user = request.user.id
    # ---------- DEVELOPING -------------
    user = User.objects.get(id=1)
    # ---------- DEVELOPING -------------
    photo_file = request.FILES.get("photo")
    if not photo_file:
        return JsonResponse({"error": "Файл 'photo' не найден"}, status=400)
    file_name = default_storage.save(f"temp_photos/{user}{photo_file.name}", photo_file)
    file_path = default_storage.path(file_name)
    meal_model = MealService.meal_photo_handler(file_path)

    meal_response = MealResponse.model_validate(meal_model)
    response = AllMealsResponse(name="meal", components=[meal_response])

    if os.path.exists(file_path):
        os.remove(file_path)

    return JsonResponse(
        {
            "success": True,
            "data": response.model_dump(),
            "message": "Meal created successfully",
        },
        status=201,
    )


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

    elif request.method == "PUT":
        # meal_id = request.json_data.get("mealId")

        try:
            meal = MealUpdate.model_validate(request.json_data)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

        with transaction.atomic():
            meal_model = MealService.update_meal(payload=meal, user=user)

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

    elif request.method == "DELETE":
        meal_id = request.GET.get("mealID")
        MealService.delete_meal(meal_id=int(meal_id))

        return JsonResponse({"status": "Meal deleted"})
