from django.http import JsonResponse
from django.urls import path
from .views import (
    create_product,
    get_product,
    list_products,
    update_product,
    delete_product,
    calculate_nutrition,
    get_product_statistics,
    api_root,
)

urlpatterns = [
    # ========== API ROOT ==========
    path("", api_root, name="api_root"),
    # ========== PRODUCT CRUD ==========
    path("products/", list_products, name="product_list"),
    path("products/create/", create_product, name="product_create"),
    path("products/<uuid:product_id>/", get_product, name="product_detail"),
    path("products/<uuid:product_id>/update/", update_product, name="product_update"),
    path("products/<uuid:product_id>/delete/", delete_product, name="product_delete"),
    # ========== PRODUCT UTILITIES ==========
    path(
        "products/<uuid:product_id>/nutrition/",
        calculate_nutrition,
        name="product_nutrition",
    ),
    path("products/statistics/", get_product_statistics, name="product_statistics"),
    # ========== API VERSIONING (опционально) ==========
    path("v1/products/", list_products, name="product_list_v1"),
    path("v1/products/create/", create_product, name="product_create_v1"),
    # ========== HEALTH CHECK ==========
    path(
        "health/", lambda request: JsonResponse({"status": "ok"}), name="health_check"
    ),
]
