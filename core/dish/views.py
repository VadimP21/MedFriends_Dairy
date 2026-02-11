"""
like web.py in Base project
"""

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.dish.schemas import DishCreate, DishResponse
from core.dish.service import DishService
from core.dish.utils import validate_json_request


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
                "message": "Product created successfully",
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


def get_product():
    pass


def list_products():
    pass


def update_product():
    pass


def delete_product():
    pass


def calculate_nutrition():
    pass


def get_product_statistics():
    pass


def api_root():
    pass
