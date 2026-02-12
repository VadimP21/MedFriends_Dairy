import json
from functools import wraps
from django.http import HttpRequest, JsonResponse


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
