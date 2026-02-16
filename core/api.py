# core/api.py
from ninja import NinjaAPI
from apps.food_diary.web import food_dairy_routes

# Создаем главное API
api = NinjaAPI(
    title="Food Diary API",
    version="1.0.0",
    description="API для дневника питания",
)

# Подключаем роуты
api.add_router("/foodDairy", food_dairy_routes)  # /api/app/vq/food/*

# Для тестирования добавим простой эндпоинт
@api.get("/health")
def health_check(request):
    return {"status": "ok", "message": "API is working"}