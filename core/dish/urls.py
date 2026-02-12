from django.http import JsonResponse
from django.urls import path
from .web.meal_views import food_diary_view, get_by_photo, get_by_voice

urlpatterns = [
    # ========== ROOT ROUTERS ==========
    path("photo/", get_by_photo, name="get_by_photo"),
    path("voice/", get_by_voice, name="get_by_voice"),
    # path(
    #     "/dataTime=<str:timestamp>",
    #     search_meal_by_date,
    #     name="search_meal_by_date",
    # ),
    path('', food_diary_view, name='food_diary'),

    # ========== DISH ROUTERS ==========
    # path(
    #     "/?dataTime=<str:timestamp>",
    #     search_dishes_by_date,
    #     name="search_dishes_by_date",
    # ),
    # path("/", hard_create_dish, name="dish_create"),
    # path("/", update_dish, name="update_dish"),
    # path("/<int:dish_id>", read_dish, name="read_dish"),
    # path("/<int:dish_id>", delete_dish, name="delete_dish"),
    # ========== CUSTOM ROUTERS ==========
    # path("dish/create/", create_dish, name="dish_create"),
]
