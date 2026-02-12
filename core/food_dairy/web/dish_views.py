"""
like web.py in Base project
"""

from datetime import datetime
from typing import List

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import TypeAdapter

from core.food_dairy.schemas.dish_schemas import DishCreate, DishResponse, DishUpdate
from core.food_dairy.service.dish_service import DishService
from core.food_dairy.utils import validate_json_request



@csrf_exempt
@validate_json_request
def hard_create_dish(
    request: HttpRequest,
):
    try:

        dish = DishCreate.model_validate(request.json_data)

        dish_model = DishService.hard_create_dish(payload=dish)
        dish_response = DishResponse.model_validate(dish_model)
        return JsonResponse(
            {
                "success": True,
                "data": dish_response.model_dump(),
                "message": "Dish created successfully",
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


def create_dish(
    request: HttpRequest,
):
    try:

        dish = DishCreate.model_validate(request.json_data)
        dish_model = DishService.create_dish(payload=dish)
        if dish_model is not None:
            dish_response = DishResponse.model_validate(dish_model)
            return JsonResponse(
                {
                    "success": True,
                    "data": dish_response.model_dump(),
                    "message": "Product created successfully",
                },
                status=201,
            )
        else:
            return JsonResponse(
                {
                    "success": True,
                    "data": dish.model_dump(),
                    "warning": "Calorie correctness check failed, you can save the product at your own risk.",
                },
                status=201,
            )
    except Exception as e:
        return JsonResponse({"success": True, "error": str(e)}, status=400)


@csrf_exempt
@validate_json_request
def read_dish(request: HttpRequest, dish_id: int):
    try:
        # проверка на принадлежность пользователя
        dish_model = DishService.get_dish_by_id(dish_id=dish_id)
        dish_response = DishResponse.model_validate(dish_model)

        return JsonResponse(
            {
                "success": True,
                "data": dish_response.model_dump(),
                "message": "Product created successfully",
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
@validate_json_request
def search_dishes_by_date(request: HttpRequest):
    try:
        # проверка на принадлежность пользователя
        date_str = request.GET.get("date")
        if not date_str:
            return JsonResponse(
                {"success": False, "error": "Parameter 'date' is required"}, status=400
            )

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid date format. Please use DD.MM.YYYY (e.g. 10.02.2026)",
                },
                status=400,
            )

        dishes_model = DishService.get_dishes_by_date(target_date=target_date)

        adapter = TypeAdapter(List[DishResponse])
        dishes = adapter.validate_python(dishes_model)

        return JsonResponse(
            {
                "success": True,
                "date": target_date.strftime("%d.%m.%Y"),
                "count": len(dishes),
                "data": [dish.model_dump() for dish in dishes],
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
@validate_json_request
def update_dish(request: HttpRequest, dish_id: int):
    try:

        dish = DishUpdate.model_validate(request.json_data)

        dish_model = DishService.update_dish(dish_id=dish_id, payload=dish)
        dish_response = DishResponse.model_validate(dish_model)

        return JsonResponse(
            {
                "success": True,
                "data": dish_response.model_dump(),
                "message": "Dish updated successfully",
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
@validate_json_request
def delete_dish(request: HttpRequest, dish_id: int):
    try:
        # проверка на принадлежность пользователя
        DishService.delete_dish(dish_id=dish_id)

        return JsonResponse(
            {
                "success": True,
                "message": "Dish successfully deleted ",
            },
            status=204,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
