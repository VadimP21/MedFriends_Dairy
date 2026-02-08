"""
like core in Base project
"""
from django.http import HttpResponse, HttpRequest

from core.dish.shcemas.ProductSchemas import ProductCreate


def create_product(
    request: HttpRequest,
    payload: ProductCreate,
    *,
    product_service: ProductService,
):
    ...


