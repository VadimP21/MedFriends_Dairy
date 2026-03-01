from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from core.mixins import MfBaseModel
from apps.accounts.models import PatientProfile


class Dish(MfBaseModel):
    """Модель конкретной порции продукта в приеме пищи"""

    name = models.CharField(
        max_length=200,
        verbose_name=_("Название продукта")
    )

    weight = models.PositiveIntegerField(
        verbose_name=_("Вес (в граммах)"),
        validators=[MinValueValidator(1)],
        help_text=_("Вес продукта в граммах"),
    )

    calories = models.PositiveIntegerField(
        verbose_name=_("Калории (ккал)"),
        help_text=_("Количество калорий в указанном весе"),
        validators=[MinValueValidator(0)],
    )

    protein = models.FloatField(
        verbose_name=_("Белки (г)"),
        help_text=_("Количество белков в указанном весе"),
        validators=[MinValueValidator(0.0)],
    )

    fat = models.FloatField(
        verbose_name=_("Жиры (г)"),
        help_text=_("Количество жиров в указанном весе"),
        validators=[MinValueValidator(0.0)],
    )

    carbohydrates = models.FloatField(
        verbose_name=_("Углеводы (г)"),
        help_text=_("Количество углеводов в указанном весе"),
        validators=[MinValueValidator(0.0)],
    )

    meal = models.ForeignKey(
        "Meal",
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name=_("Прием пищи"),
    )

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")

    def __str__(self):
        return f"{self.name} ({self.weight}g)"

    def checking_correctness_of_calories(self) -> bool:
        """Проверка корректности калорий"""
        estimated_calories = (
                (self.protein * 4) + (self.carbohydrates * 4) + (self.fat * 9)
        )
        if abs(self.calories - estimated_calories) > self.calories * 0.3:
            return True
        return False


class Meal(MfBaseModel):
    """Прием пищи из нескольких блюд"""

    class MealTypes(models.TextChoices):
        BREAKFAST = 'завтрак', 'завтрак'
        LUNCH = 'обед', 'обед'
        DINNER = 'ужин', 'ужин'
        SNACK = 'перекус', 'перекус'

    # MEAL_TYPE_VALUES = [choice[0] for choice in MealTypes.choices]

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="meals",
        verbose_name=_("Пациент"),
    )

    name = models.CharField(
        max_length=20,
        choices=MealTypes.choices,
        verbose_name=_("Тип приема пищи"),
        help_text=_("Завтрак, Обед, Ужин, Перекус"),
    )

    meal_date = models.DateField(
        verbose_name=_("Дата приема пищи"),
        help_text=_("Дата, когда был прием пищи"),
    )

    meal_time = models.TimeField(
        verbose_name=_("Время приема пищи"),
        help_text=_("Время приема пищи"),
    )

    class Meta:
        verbose_name = _("Прием пищи")
        verbose_name_plural = _("Приемы пищи")
        ordering = ['-meal_date', '-meal_time']
        indexes = [
            models.Index(fields=['patient', 'meal_date']),
        ]

    def __str__(self):
        return f"{self.get_name_display()} - {self.meal_date}"

    @property
    def total_weight(self):
        return sum(component.weight for component in self.components.all())

    @property
    def total_calories(self):
        return sum(component.calories for component in self.components.all())

    @property
    def total_protein(self):
        return sum(component.protein for component in self.components.all())

    @property
    def total_fat(self):
        return sum(component.fat for component in self.components.all())

    @property
    def total_carbohydrates(self):
        return sum(component.carbohydrates for component in self.components.all())


class MealTimeSlot(MfBaseModel):
    """Интервалы времени для типов приемов пищи"""

    title = models.CharField(
        max_length=20,
        choices=Meal.MealTypes,
        unique=True,
        verbose_name=_("Тип приема пищи")
    )

    start_hour = models.PositiveSmallIntegerField(
        _("Час начала (0-23)"),
        validators=[MinValueValidator(0), MaxValueValidator(23)]
    )

    end_hour = models.PositiveSmallIntegerField(
        _("Час окончания (0-23)"),
        validators=[MinValueValidator(0), MaxValueValidator(23)]
    )

    class Meta:
        verbose_name = _("Интервал приема пищи")
        verbose_name_plural = _("Интервалы приема пищи")
        ordering = ["start_hour"]

    def __str__(self):
        return f"{self.get_title_display()}: {self.start_hour}:00 - {self.end_hour}:00"
