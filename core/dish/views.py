"""
like core in Base project
"""
import json

from django.http import HttpResponse, HttpRequest, JsonResponse

from core.dish.models import Product
from core.dish.service import ProductService
from core.dish.shcemas.product_schemas import ProductCreate, ProductResponse


def create_product(
        request: HttpRequest,
        product_service: ProductService,
):
    body_data = json.loads(request.body.decode('utf-8'))
    validated_product = ProductCreate(**body_data)
    # validated_product = ProductCreate(request.body.decode())


    response_data = product_service.create_product(payload=validated_product)

    response_dto = ProductResponse.form_orm(response_data)

    return JsonResponse(response_dto.dict, status=201)