from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Dish(models.Model):
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
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.name} (weight: {self.weight}, score: {self.score})"


class Meal(models.Model):
    """Прием пищи из нескольких блюд"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="meals",
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время приема пищи",
        help_text="Заполняется автоматически на основе локального времени "
        "на устройстве пользователя.	Возможно изменение вручную",
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Тип приема пищи",
        help_text="Завтрак, Обед, Ужин, Перекус/другое",
    )

    portion_size = models.TextField(
        verbose_name="Размер порции",
        help_text="Текстовое описание размера порции ('Стандартная')",
    )

    description = models.CharField(
        max_length=200, verbose_name="Описание продукта", blank=True, null=True
    )

    class Meta:
        verbose_name = "Прием пищи"
        verbose_name_plural = "Приемы пищи"

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def total_weight(self):
        """Суммирует вес всех компонентов приема пищи"""
        return sum(component.weight for component in self.components.all())

    @property
    def total_calories(self):
        """Суммирует калории всех компонентов"""
        return sum(component.calories for component in self.components.all())

    @property
    def total_protein(self):
        """Суммирует белки всех компонентов"""
        return sum(component.protein for component in self.components.all())

    @property
    def total_fat(self):
        """Суммирует жиры всех компонентов"""
        return sum(component.fat for component in self.components.all())

    @property
    def total_carbohydrates(self):
        """Суммирует углеводы всех компонентов"""
        return sum(component.carbohydrates for component in self.components.all())

    @property
    def avg_score(self):
        """Средний индекс здоровья для всего приема пищи"""
        components = self.components.all()
        if not components:
            return 0
        return sum(c.score for c in components) / components.count()
