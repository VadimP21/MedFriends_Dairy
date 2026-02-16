# apps/food/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.mixins import UUIDModel, TimeStampedModel
from apps.accounts.models import PatientProfile


class Dish(UUIDModel, TimeStampedModel):
    """Модель конкретной порции продукта в приеме пищи"""

    name = models.CharField(max_length=200, verbose_name="Название продукта")

    weight = models.PositiveIntegerField(
        verbose_name="Вес (в граммах)",
        validators=[MinValueValidator(1)],
        help_text="Вес продукта в граммах",
    )

    calories = models.PositiveIntegerField(
        verbose_name="Калории (ккал)",
        help_text="Количество калорий в указанном весе",
        validators=[MinValueValidator(0)],
    )
    protein = models.FloatField(
        verbose_name="Белки (г)",
        help_text="Количество белков в указанном весе",
        validators=[MinValueValidator(0.0)],
    )
    fat = models.FloatField(
        verbose_name="Жиры (г)",
        help_text="Количество жиров в указанном весе",
        validators=[MinValueValidator(0.0)],
    )
    carbohydrates = models.FloatField(
        verbose_name="Углеводы (г)",
        help_text="Количество углеводов в указанном весе",
        validators=[MinValueValidator(0.0)],
    )

    score = models.FloatField(
        verbose_name="Индекс «здорового питания»",
        help_text="Оценка того, насколько продукт полезен для организма",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    description = models.TextField(
        verbose_name="Описание продукта", blank=True, null=True
    )

    meal = models.ForeignKey(
        "Meal",
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name="Прием пищи",
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

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


class Meal(UUIDModel, TimeStampedModel):
    """Прием пищи из нескольких блюд"""

    MEAL_TYPES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
        ('snack', 'Перекус'),
    ]

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="meals",
        verbose_name="Пациент",
    )
    name = models.CharField(
        max_length=20,
        choices=MEAL_TYPES,
        blank=True,
        verbose_name="Тип приема пищи",
        help_text="Завтрак, Обед, Ужин, Перекус/другое", )

    meal_date = models.DateField(
        verbose_name="Дата приема пищи",
        help_text="Дата, когда был прием пищи",
    )
    meal_time = models.TimeField(
        verbose_name="Время приема пищи",
        help_text="Время приема пищи",
    )

    portion_size = models.TextField(
        verbose_name="Размер порции",
        help_text="Текстовое описание размера порции",
    )

    description = models.CharField(
        max_length=200,
        verbose_name="Описание",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Прием пищи"
        verbose_name_plural = "Приемы пищи"
        ordering = ['-meal_date', '-meal_time']
        indexes = [
            models.Index(fields=['patient', 'meal_date']),
        ]

    def __str__(self):
        return f"{self.get_meal_type_display()} - {self.meal_date}"

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

    @property
    def avg_score(self):
        components = self.components.all()
        if not components:
            return 0.0
        return sum(c.score for c in components) / components.count()


class MealTimeSlot(UUIDModel, TimeStampedModel):
    """Интервалы времени для типов приемов пищи"""

    title = models.CharField(
        max_length=20,
        choices=Meal.MEAL_TYPES,
        unique=True,
        verbose_name="Тип приема пищи"
    )
    start_hour = models.PositiveSmallIntegerField(
        "Час начала (0-23)",
        validators=[MinValueValidator(0), MaxValueValidator(23)]
    )
    end_hour = models.PositiveSmallIntegerField(
        "Час окончания (0-23)",
        validators=[MinValueValidator(0), MaxValueValidator(23)]
    )

    class Meta:
        verbose_name = "Интервал приема пищи"
        verbose_name_plural = "Интервалы приема пищи"
        ordering = ["start_hour"]

    def __str__(self):
        return f"{self.get_title_display()}: {self.start_hour}:00 - {self.end_hour}:00"
