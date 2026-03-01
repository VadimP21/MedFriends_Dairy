from ninja import NinjaAPI
from apps.food_diary.web import user_routers

# Создаем главное API
api = NinjaAPI(
    title="Food Diary API",
    version="1.0.0",
    description="API для дневника питания",
)

# Подключаем роуты
api.add_router("food_diary/", user_routers)  # /api/app/v1/food_diary/*

# Для тестирования добавим простой эндпоинт
@api.get("/health")
def health_check(request):
    return {"status": "ok", "message": "API is working"}