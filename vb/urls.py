from django.contrib import admin
from django.urls import path, include
from voice_app.urls import urlpatterns as voice_app_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(voice_app_urls)),
]
