"""
like web.py in Base project
"""

from datetime import datetime
from typing import List

from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pydantic import TypeAdapter

from core.dish.service.meal_service import MealService
from core.dish.schemas.dish_schemas import DishCreate, DishResponse, DishUpdate
from core.dish.schemas.meal_schemas import MealCreate, MealResponse
from core.dish.utils import validate_json_request, validate_json_body


@validate_json_body
@require_http_methods(["GET"])
def get_by_photo(): ...


@validate_json_body
@require_http_methods(["GET"])
def get_by_voice(): ...


@validate_json_body
@require_http_methods(["GET"])
def get_by_id(): ...


@validate_json_body
@require_http_methods(["POST", "GET", "PUT", "DELETE"])
def food_diary_view(request: HttpRequest):
    user = request.user.id

    if request.method == "POST":
        try:
            meal = MealCreate.model_validate(request.json_data)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

        with transaction.atomic():
            meal_model = MealService.create_meal(payload=meal, user=user)
            meal_response = MealResponse.model_validate(meal_model)
        return JsonResponse(
            {
                "success": True,
                "data": meal_response.model_dump(),
                "message": "Meal created successfully",
            },
            status=201,
        )


    elif request.method == "GET":
        date_str = request.GET.get("dateTime")
        if not date_str:
            return JsonResponse({"success": False, "error": "dateTime parameter is required"}, status=400)

        try:
            if date_str.isdigit():
                target_date = datetime.fromtimestamp(int(date_str)).date()
            else:
                target_date = datetime.strptime(date_str, "%d.%m.%Y").date()

        except ValueError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid date format. Please use DD.MM.YYYY (e.g. 10.02.2026)",
                },
                status=400,
            )

        meals_model = MealService.get_meals_by_date(target_date=target_date, user=user)

        adapter = TypeAdapter(List[DishResponse])
        meals = adapter.validate_python(meals_model)

        return JsonResponse(
            {
                "success": True,
                "data": [meal.model_dump() for meal in meals],
                "message": "Meal created successfully",
            },
            status=200,
        )

