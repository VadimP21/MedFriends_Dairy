import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Модель категории продуктов"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-идентификатор")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель единицы продукта с разделенным КБЖУ"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Идентификатор"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название продукта"
    )
    average_portion = models.PositiveIntegerField(
        verbose_name="Средний размер порции (в граммах)",
        help_text="Средняя рекомендуемая порция в граммах",
        default=100
    )
    description = models.TextField(
        verbose_name="Описание продукта",
        blank=True,
        null=True
    )

    calories = models.PositiveIntegerField(
        verbose_name="Калории (ккал)",
        help_text="Количество калорий в 100 граммах продукта",
        validators=[MinValueValidator(0)]
    )
    protein = models.FloatField(
        verbose_name="Белки (г)",
        help_text="Количество белков в 100 граммах продукта",
        validators=[MinValueValidator(0.0)]
    )
    fat = models.FloatField(
        verbose_name="Жиры (г)",
        help_text="Количество жиров в 100 граммах продукта",
        validators=[MinValueValidator(0.0)]
    )
    carbohydrates = models.FloatField(
        verbose_name="Углеводы (г)",
        help_text="Количество углеводов в 100 граммах продукта",
        validators=[MinValueValidator(0.0)]
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Категория"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['calories']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

class MealType(models.Model):
    """Типы приемов пищи"""
    BREAKFAST = 'breakfast'
    LUNCH = 'lunch'
    DINNER = 'dinner'
    SNACK = 'snack'
    OTHER = 'other'

    MEAL_TYPE_CHOICES = [
        (BREAKFAST, 'Завтрак'),
        (LUNCH, 'Обед'),
        (DINNER, 'Ужин'),
        (SNACK, 'Перекус'),
        (OTHER, 'Другое'),
    ]

    name = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
        unique=True,
        verbose_name="Тип приема пищи"
    )
    default_name = models.CharField(
        max_length=100,
        verbose_name="Название по умолчанию"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки"
    )

    class Meta:
        verbose_name = "Тип приема пищи"
        verbose_name_plural = "Типы приемов пищи"
        ordering = ['order', 'name']

    def __str__(self):
        return self.get_name_display()

class Dish(models.Model):
    """Блюдо из определенного веса продукта"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='dishes',
        verbose_name="Продукт"
    )
    weight = models.PositiveIntegerField(
        verbose_name="Вес (в граммах)",
        validators=[MinValueValidator(1)],
        help_text="Вес продукта в граммах"
    )

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ['-id']

    def __str__(self):
        return f"{self.product.name} - {self.weight}г"


class Meal(models.Model):
    """Прием пищи из нескольких блюд"""
    id = models.AutoField(primary_key=True, verbose_name="ID")
    meal_type = models.ForeignKey(
        MealType,
        on_delete=models.SET_DEFAULT,
        verbose_name="Тип приема пищи"
    )
    custom_meal_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Пользовательский тип",
        help_text="Если не выбрано из списка. Приоритет выше, чем автоопределение по времени."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время приема пищи"
    )
    dishes = models.ManyToManyField(
        Dish,
        related_name='meals',
        verbose_name="Блюда",
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meals',
        verbose_name="Пользователь"
    )

    total_calories = models.PositiveIntegerField(
        verbose_name="Общие калории",
        default=0,
        help_text="Суммарная калорийность приема пищи"
    )
    total_protein = models.FloatField(
        verbose_name="Общие белки",
        default=0.0,
        help_text="Суммарные белки приема пищи"
    )
    total_fat = models.FloatField(
        verbose_name="Общие жиры",
        default=0.0,
        help_text="Суммарные жиры приема пищи"
    )
    total_carbohydrates = models.FloatField(
        verbose_name="Общие углеводы",
        default=0.0,
        help_text="Суммарные углеводы приема пищи"
    )

    notes = models.TextField(
        verbose_name="Заметки",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Прием пищи"
        verbose_name_plural = "Приемы пищи"
        # ordering = ['-created_at']
        # indexes = [
        #     models.Index(fields=['user', 'created_at']),
        #     models.Index(fields=['meal_type']),
        #     models.Index(fields=['total_calories']),
        # ]