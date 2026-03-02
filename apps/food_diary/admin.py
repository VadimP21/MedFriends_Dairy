from django.contrib import admin
from django.utils.html import format_html

from apps.food_diary.models import MealTimeSlot


class MealTimeSlotAdmin(admin.ModelAdmin):
    """Админка для интервалов времени приемов пищи"""

    list_display = (
        "title_with_icon",
        "time_range",
        "duration_hours",
        "is_valid_interval",
    )

    list_filter = ("title",)

    search_fields = ("title",)

    fieldsets = (
        (
            "Настройка интервала",
            {
                "fields": (
                    "title",
                    ("start_hour", "end_hour"),
                )
            },
        ),
        (
            "Пояснение",
            {
                "fields": (),
                "description": """
                <strong>Как работают интервалы:</strong><br>
                - Завтрак: блюда, добавленные в этот период<br>
                - Обед: блюда, добавленные в этот период<br>
                - Ужин: блюда, добавленные в этот период<br>
                - Перекус: блюда вне основных интервалов или специально отмеченные
            """,
            },
        ),
    )

    def title_with_icon(self, obj):
        """Название с иконкой"""
        icons = {
            "breakfast": "🍳",
            "lunch": "🍲",
            "dinner": "🍽️",
            "snack": "🍎",
        }
        icon = icons.get(obj.title, "📋")
        return format_html("{} {}", icon, obj.get_title_display())

    title_with_icon.short_description = "Тип"
    title_with_icon.admin_order_field = "title"

    def time_range(self, obj):
        """Диапазон времени"""
        return f"{obj.start_hour:02d}:00 - {obj.end_hour:02d}:00"

    time_range.short_description = "Временной диапазон"

    def duration_hours(self, obj):
        """Длительность в часах"""
        duration = obj.end_hour - obj.start_hour
        if duration < 0:
            duration += 24
        return f"{duration} ч."

    duration_hours.short_description = "Длительность"

    def is_valid_interval(self, obj):
        """Проверка корректности интервала"""
        if obj.start_hour == obj.end_hour:
            return format_html('<span style="color:red;">❌ Начало = Конец</span>')
        if (
            obj.start_hour < 0
            or obj.start_hour > 23
            or obj.end_hour < 0
            or obj.end_hour > 23
        ):
            return format_html('<span style="color:red;">❌ Вне диапазона 0-23</span>')
        return format_html('<span style="color:green;">✓ Корректно</span>')

    is_valid_interval.short_description = "Проверка"

    class Media:
        css = {"all": ("admin/css/forms.css",)}


admin.site.register(MealTimeSlot, MealTimeSlotAdmin)
