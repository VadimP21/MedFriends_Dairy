from django.contrib import admin

from apps.accounts.models import PatientProfile, User

admin.site.site_header = "Административный Интерфейс"
admin.site.index_title = "Food Diary app"


class UserAdmin(admin.ModelAdmin):
    """
    Админка для пользователя
    """

    list_display = ("first_name", "last_name", "phone", "email")


class PatientProfileAdmin(admin.ModelAdmin):
    """
    Админка для профиля пациента
    """

    list_display = ("user", "height", "weight")
    search_fields = ("user", "first_name", "last_name", "phone", "email")


admin.site.register(PatientProfile, PatientProfileAdmin)
admin.site.register(User, UserAdmin)
