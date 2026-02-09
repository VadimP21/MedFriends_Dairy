"""
like core in Base project
"""
import json

from django.http import HttpRequest, JsonResponse

from core.dish.service import ProductService
from core.dish.shcemas.product_schemas import ProductCreate, ProductResponse
from core.dish.utils import validate_json_request


@validate_json_request
def create_product(
        request: HttpRequest,
):
    try:
        validated_data = ProductCreate.model_validate(json.loads(request.body))

        product = ProductService.create_product(payload=validated_data)

        response_dto = ProductResponse.model_validate(product)

        return JsonResponse(
            {
                'success': True,
                'data': response_dto.model_dump(),
                'message': 'Product created successfully'
            },
            status=201
        )
    except Exception as e:
        return JsonResponse(
            {
                'success': False,
                'error': str(e)
            },
            status=400
        )
