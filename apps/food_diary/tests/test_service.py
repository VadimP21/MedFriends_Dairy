import pytest
import datetime
from unittest.mock import patch, AsyncMock
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.food_diary.core import MealService
from apps.food_diary.schemas import MealCreateIn, MealUpdateIn, DishCreateIn


@pytest.mark.django_db
class TestMealService:
    """Тесты для MealService"""

    def test_create_meal_success(
        self, mock_patient, mock_meal_data, mock_meal, mock_dish_queryset
    ):
        """Тест успешного создания приема пищи"""
        # Setup
        payload = MealCreateIn(**mock_meal_data)

        with patch(
            "apps.food_diary.services.Meal.objects.create", return_value=mock_meal
        ) as mock_create, patch(
            "apps.food_diary.services.Dish.objects.bulk_create"
        ) as mock_bulk_create, patch(
            "apps.food_diary.services.Meal.objects.prefetch_related"
        ) as mock_prefetch, patch(
            "apps.food_diary.services.get_meal_name_by_time"
        ) as mock_get_name:
            mock_get_name.return_value = "завтрак"
            mock_prefetch.return_value.get.return_value = mock_meal

            # Execute
            result = MealService.create_meal(patient=mock_patient, payload=payload)

            # Assert
            mock_create.assert_called_once()
            mock_bulk_create.assert_called_once()
            assert result == mock_meal

    def test_create_meal_unique_constraint_violation(
        self, mock_patient, mock_meal_data
    ):
        """Тест ошибки уникальности при создании"""
        payload = MealCreateIn(**mock_meal_data)

        with patch("apps.food_diary.services.Meal.objects.create") as mock_create:
            mock_create.side_effect = IntegrityError("unique constraint failed")

            with pytest.raises(ValidationError) as exc:
                MealService.create_meal(patient=mock_patient, payload=payload)

            assert "already exists" in str(exc.value)

    def test_update_meal_success(self, mock_patient, mock_meal, mock_update_data):
        """Тест успешного обновления приема пищи"""
        # Setup
        payload = MealUpdateIn(**mock_update_data)

        with patch(
            "apps.food_diary.services.get_object_or_404", return_value=mock_meal
        ) as mock_get, patch(
            "apps.food_diary.services.Meal.objects.prefetch_related"
        ) as mock_prefetch:
            mock_prefetch.return_value.get.return_value = mock_meal

            # Execute
            result = MealService.update_meal(patient=mock_patient, payload=payload)

            # Assert
            mock_get.assert_called_once()
            mock_meal.save.assert_called_once()
            assert result == mock_meal

    def test_update_meal_not_found(self, mock_patient, mock_update_data):
        """Тест обновления несуществующего приема пищи"""
        payload = MealUpdateIn(**mock_update_data)

        with patch("apps.food_diary.services.get_object_or_404") as mock_get:
            mock_get.side_effect = Exception("Meal not found")

            with pytest.raises(Exception):
                MealService.update_meal(patient=mock_patient, payload=payload)

    def test_delete_meal_success(self, mock_patient, mock_meal):
        """Тест успешного удаления"""
        with patch(
            "apps.food_diary.services.get_object_or_404", return_value=mock_meal
        ) as mock_get:
            MealService.delete_meal(patient=mock_patient, meal_id="test-id")

            mock_get.assert_called_once()
            mock_meal.delete.assert_called_once()

    def test_get_meals_by_date(self, mock_patient, mock_meals_queryset):
        """Тест получения приемов пищи по дате"""
        target_date = datetime.date.today()

        with patch(
            "apps.food_diary.services.Meal.objects.filter",
            return_value=mock_meals_queryset,
        ):
            result = MealService.get_meals_by_date(
                patient=mock_patient, target_date=target_date
            )

            assert result == mock_meals_queryset

    def test_get_meals_by_date_range(self, mock_patient, mock_meals_queryset):
        """Тест получения приемов пищи за период"""
        from_date = datetime.date.today() - datetime.timedelta(days=7)
        to_date = datetime.date.today()

        with patch(
            "apps.food_diary.services.Meal.objects.filter",
            return_value=mock_meals_queryset,
        ) as mock_filter:
            result = MealService.get_meals_by_date_range(
                patient=mock_patient, from_date=from_date, to_date=to_date
            )

            assert result == mock_meals_queryset
            mock_filter.assert_called_once_with(patient=mock_patient)

    def test_get_meal_by_id_success(self, mock_patient, mock_meal):
        """Тест получения приема пищи по ID"""
        with patch(
            "apps.food_diary.services.get_object_or_404", return_value=mock_meal
        ) as mock_get:
            result = MealService.get_meal_by_id(patient=mock_patient, meal_id="test-id")

            mock_get.assert_called_once()
            assert result == mock_meal

    @pytest.mark.asyncio
    async def test_get_meal_by_photo_success(
        self, mock_patient, mock_dishes_data, mock_meal
    ):
        """Тест успешного создания приема пищи по фото"""
        image_bytes = b"fake_image_data"

        with patch(
            "apps.food_diary.services.food_analysis_service.analyze_food_image",
            new_callable=AsyncMock,
        ) as mock_analyze, patch(
            "apps.food_diary.services.MealService.create_meal"
        ) as mock_create_meal:
            mock_analyze.return_value = [
                DishCreateIn(**dish) for dish in mock_dishes_data
            ]
            mock_create_meal.return_value = mock_meal

            result = await MealService.get_meal_by_photo(
                patient=mock_patient, image_bytes=image_bytes, name="ужин"
            )

            mock_analyze.assert_called_once_with(image=image_bytes)
            mock_create_meal.assert_called_once()
            assert result == mock_meal

    @pytest.mark.asyncio
    async def test_get_meal_by_photo_no_dishes(self, mock_patient):
        """Тест ошибки при отсутствии блюд на фото"""
        image_bytes = b"fake_image_data"

        with patch(
            "apps.food_diary.services.food_analysis_service.analyze_food_image",
            new_callable=AsyncMock,
        ) as mock_analyze:
            mock_analyze.return_value = []

            with pytest.raises(ValidationError) as exc:
                await MealService.get_meal_by_photo(
                    patient=mock_patient, image_bytes=image_bytes
                )

            assert "No dishes detected" in str(exc.value)

    @pytest.mark.asyncio
    async def test_get_meal_by_photo_analysis_error(self, mock_patient):
        """Тест ошибки при анализе фото"""
        image_bytes = b"fake_image_data"

        with patch(
            "apps.food_diary.services.food_analysis_service.analyze_food_image",
            new_callable=AsyncMock,
        ) as mock_analyze:
            mock_analyze.side_effect = Exception("API error")

            with pytest.raises(ValidationError) as exc:
                await MealService.get_meal_by_photo(
                    patient=mock_patient, image_bytes=image_bytes
                )

            assert "Error analyzing photo" in str(exc.value)

    def test_get_meals_by_date_range_and_type(self, mock_patient, mock_meals_queryset):
        """Тест получения приемов пищи с фильтрацией по типу"""
        from_date = datetime.date.today() - datetime.timedelta(days=7)
        to_date = datetime.date.today()
        meal_type = "breakfast"

        with patch(
            "apps.food_diary.services.Meal.objects.filter",
            return_value=mock_meals_queryset,
        ) as mock_filter:
            result = MealService.get_meals_by_date_range_and_type(
                patient=mock_patient,
                from_date=from_date,
                to_date=to_date,
                meal_type=meal_type,
            )

            assert result == mock_meals_queryset
            mock_filter.assert_called_once_with(patient=mock_patient)
