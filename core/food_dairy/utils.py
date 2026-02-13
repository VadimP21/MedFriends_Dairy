import json
from datetime import datetime
from functools import wraps

from django.core.cache import cache
from django.http import HttpRequest, JsonResponse

from core.food_dairy.models import MealTimeSlot


def validate_json_request(func):
    """Декоратор для валидации JSON запросов, отдает dict"""

    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.method != "POST":
            return JsonResponse({"error": "Method not allowed"}, status=405)

        if not request.body:
            return JsonResponse({"error": "Request body is empty"}, status=400)

        try:
            body_unicode = request.body.decode("utf-8")
            print(f"Body: {request.body.decode()}")
            data = json.loads(request.body.decode("utf-8").strip())
        except json.JSONDecodeError as e:
            return JsonResponse(
                {
                    "error": "Invalid JSON format",
                    "details": str(e),
                    "received_body": body_unicode,  # Временно для отладки
                },
                status=400,
            )

        request.json_data = data
        return func(request, *args, **kwargs)

    return wrapper


import json
from functools import wraps
from django.http import HttpRequest, JsonResponse


def validate_json_body(func):
    """Парсит JSON и сохраняет в request.json_data для методов с телом запроса"""

    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.method in ["POST", "PUT", "PATCH"]:
            if not request.body:
                return JsonResponse({"error": "Request body is empty"}, status=400)
            try:
                request.json_data = json.loads(request.body.decode("utf-8").strip())
            except json.JSONDecodeError as e:
                return JsonResponse(
                    {"error": "Invalid JSON", "details": str(e)}, status=400
                )
        return func(request, *args, **kwargs)

    return wrapper


def get_meal_name_by_time(timestamp: datetime):
    slots = cache.get("meal_time_slots")

    if slots is None:
        # Если в кэше нет, берем из БД и сохраняем в кэш на 24 часа
        slots = list(MealTimeSlot.objects.all())
        cache.set("meal_time_slots", slots, 60 * 60 * 24)

    hour = timestamp.hour

    for slot in slots:
        if slot.start_hour <= hour < slot.end_hour:
            return slot.get_title_display().lower()

    return "перекус"


def is_dat_is_valid(date_str: str):
    if date_str.isdigit():
        target_date = datetime.fromtimestamp(int(date_str)).date()
    else:
        target_date = datetime.strptime(date_str, "%d.%m.%Y").date()

    return target_date
