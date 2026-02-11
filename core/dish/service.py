from core.dish.models import Dish, Meal
from core.dish.schemas import DishCreate, MealCreate
from core.dish.utils import cpfc_is_correct


class MealService:

    @staticmethod
    def create_meal(payload: MealCreate) -> Meal:
        meal = Meal.objects.create(**payload.model_dump())

        return meal


class DishService:

    @staticmethod
    def hard_create_dish(payload: DishCreate) -> Dish:
        dish_model = Dish.objects.create(**payload.model_dump())

        return dish_model

    @staticmethod
    def create_dish(payload: DishCreate) -> Dish | None:

        dish_model = Dish(**payload.model_dump())
        if dish_model.checking_correctness_of_calories():
            dish_model = Dish.objects.create(**payload.model_dump())
            return dish_model
        return None

    @staticmethod
    def read_dish(payload: ProductCreate) -> Dish:
        product_data = payload.model_dump()

        product = Product.objects.create(**product_data)

        return product

    @staticmethod
    def update_dish(payload: ProductCreate) -> Dish:
        product_data = payload.model_dump()

        product = Product.objects.create(**product_data)

        return product
