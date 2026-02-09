import json
from functools import wraps
from django.http import HttpRequest, JsonResponse


def validate_json_request(func):
    """Декоратор для валидации JSON запросов"""

    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse(
                {'error': 'Method not allowed'},
                status=405
            )

        if not request.body:
            return JsonResponse(
                {'error': 'Request body is empty'},
                status=400
            )

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON format'},
                status=400
            )

        request.json_data = data
        return func(request, *args, **kwargs)

    return wrapper
