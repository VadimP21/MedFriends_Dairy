from django.contrib.auth.models import AbstractUser
from django.db import models
from core.mixins import UUIDModel, TimeStampedModel


class User(AbstractUser, UUIDModel, TimeStampedModel):
    """Кастомная модель пользователя"""

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_patient = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class PatientProfile(UUIDModel, TimeStampedModel):
    """Профиль пациента"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )

    # Дополнительные поля профиля
    birth_date = models.DateField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True, verbose_name="Рост (см)")
    weight = models.FloatField(null=True, blank=True, verbose_name="Вес (кг)")

    # Персональная информация (как в основном проекте)
    personal_info = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Профиль пациента"
        verbose_name_plural = "Профили пациентов"

    def __str__(self):
        return f"Patient: {self.user.email}"