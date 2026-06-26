"""
Представления (Views) для приложения buildings
Обрабатывают HTTP-запросы к API зданий
"""

from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Building
from .serializers import BuildingSerializer


class BuildingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операций с зданиями
    Поддерживает GeoJSON и фильтр по расстоянию
    """

    # Базовый запрос: все здания
    queryset = Building.objects.all()

    # Сериализатор для преобразования данных
    serializer_class = BuildingSerializer

    def list(self, request, *args, **kwargs):
        """
        Переопределяем метод list() для возврата FeatureCollection
        По спецификации GeoJSON коллекция объектов — это FeatureCollection
        """
        # Получаем отфильтрованный queryset (с учётом параметров ?lon=&lat=&dist=)
        queryset = self.filter_queryset(self.get_queryset())

        # Сериализуем объекты
        serializer = self.get_serializer(queryset, many=True)

        # Возвращаем объект типа FeatureCollection
        return Response({
            "type": "FeatureCollection",
            "features": serializer.data
        })

    def get_queryset(self):
        """
        Добавляем фильтрацию по расстоянию от точки
        Параметры: ?lon=долгота&lat=широта&dist=радиус_в_метрах
        """
        # Получаем базовый queryset от родителя
        queryset = super().get_queryset()

        # Читаем параметры из GET-запроса
        lon = self.request.query_params.get('lon')
        lat = self.request.query_params.get('lat')
        dist = self.request.query_params.get('dist')

        # Если все три параметра есть — применяем фильтр
        if lon and lat and dist:
            try:
                # Создаём точку в системе координат WGS84
                point = Point(float(lon), float(lat), srid=4326)

                # Переводим расстояние в метры (float)
                distance_m = float(dist)

                # Аннотируем queryset расстоянием от точки до каждого здания
                # Distance() автоматически использует geography для расчётов в метрах
                queryset = queryset.annotate(
                    distance=Distance('geom', point)
                ).filter(
                    # Фильтруем: оставляем только здания, попадающие в радиус
                    # (полностью или частично — как требует задание)
                    distance__lte=distance_m
                )

            except (ValueError, TypeError):
                # Если параметры некорректны (не числа) — игнорируем фильтр
                # и возвращаем все объекты (безопасное поведение)
                pass

        return queryset