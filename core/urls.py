from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/app/v1/', api.urls),  # Все API доступны по /api/app/v1/
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)