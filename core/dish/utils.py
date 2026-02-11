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
            data = json.loads(request.body.decode().strip())
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
