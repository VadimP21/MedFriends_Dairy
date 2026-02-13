from django.contrib import admin
from .models import MealTimeSlot


@admin.register(MealTimeSlot)
class MealTimeSlotAdmin(admin.ModelAdmin):
    list_display = ("title", "start_hour", "end_hour")
