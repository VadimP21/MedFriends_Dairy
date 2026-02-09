from core.dish.models import Product
from core.dish.shcemas.product_schemas import ProductCreate


class ProductService:
    @staticmethod
    def create_product(payload: ProductCreate) -> Product:
        product_data = payload.model_dump()

        product = Product.objects.create(**product_data)

        return product
