"""
like core in Base project
"""
from uuid import UUID

from django.http import HttpResponse, HttpRequest

from core.dish.models import Product
from core.dish.shcemas.product_schemas import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    def create_product(payload: ProductCreate,
                       ) -> Product | None:
        product_data = payload.dict(exclude_unset=True)

        #  проверка инвариантов продукта через models.Product  (допустимое кол-во КБЖУ, )

        # product = Product(**product_data)
        # if product.check_CPFC_correctionally():
        #     product, _ = product.objects.update_or_create(**product_data)
        #
        #     return product
        # return None

        product = Product.objects.create(**product_data)

        return product

    @staticmethod
    def get_product(product_id: UUID) -> Product:
       return Product.objects.filter(id=product_id).first()

    @staticmethod
    def update_product(product_for_update: Product, payload: ProductUpdate):



