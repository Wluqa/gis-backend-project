"""
Настройка URL-адресов для проекта GIS
Маршрутизация запросов к API и админке
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from buildings.views import BuildingViewSet

# Создаём роутер для автоматической генерации URL для ViewSet
router = DefaultRouter()
# r'buildings' — префикс URL,
# BuildingViewSet — наш класс с логикой,
# basename='building' — имя для reverse-поиска
router.register(r'buildings', BuildingViewSet, basename='building')

# Основные маршруты проекта
urlpatterns = [
    # Админ-панель Django (доступна по /admin/)
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
]