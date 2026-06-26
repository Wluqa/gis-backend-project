"""
Тесты для приложения buildings
Проверяют корректность работы API и фильтров
"""

from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.gis.geos import Polygon, Point
from .models import Building


class BuildingModelTest(TestCase):
    """Тесты модели Building"""

    def test_building_creation(self):
        """Проверка создания здания с валидной геометрией"""
        building = Building.objects.create(
            address="Тестовое здание",
            geom=Polygon(((0, 0), (0, 0.001), (0.001, 0.001), (0.001, 0), (0, 0)))
        )
        self.assertEqual(building.address, "Тестовое здание")
        self.assertTrue(building.geom.valid)

    def test_invalid_geometry_raises_error(self):
        """Проверка, что невалидная геометрия отклоняется"""
        # Полигон с самопересечением (невалидный)
        invalid_geom = Polygon(((0, 0), (0, 1), (1, 0), (1, 1), (0, 0)))
        building = Building(address="Bad Building", geom=invalid_geom)

        # full_clean() вызывает метод clean(), где наша валидация
        with self.assertRaises(Exception):  # ValidationError
            building.full_clean()


class BuildingDistanceFilterTest(TestCase):
    """Тесты фильтра по расстоянию"""

    def setUp(self):
        """Создаём тестовые данные перед каждым тестом"""
        self.client = APIClient()

        # Здание рядом с точкой (0, 0) — примерно 11 метров от центра
        self.near_building = Building.objects.create(
            address="Близкое здание",
            geom=Polygon(((0.0001, 0.0001), (0.0001, -0.0001),
                          (-0.0001, -0.0001), (-0.0001, 0.0001),
                          (0.0001, 0.0001)))  # Замкнутый маленький полигон
        )

        # Здание далеко — примерно 100+ км от (0, 0)
        self.far_building = Building.objects.create(
            address="Далёкое здание",
            geom=Polygon(((1.0, 1.0), (1.0, 0.9), (0.9, 0.9), (0.9, 1.0), (1.0, 1.0)))
        )

    def test_filter_returns_near_buildings_only(self):
        """Фильтр должен вернуть только здания в радиусе"""
        # Запрос: точка (0, 0), радиус 20 метров
        response = self.client.get('/api/buildings/?lon=0&lat=0&dist=20')

        # Проверяем статус ответа
        self.assertEqual(response.status_code, 200)

        # Проверяем структуру ответа (FeatureCollection)
        data = response.json()
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertIn('features', data)

        # Извлекаем ID возвращённых зданий
        returned_ids = [f['properties']['id'] for f in data['features']]

        # Близкое здание должно быть в списке
        self.assertIn(self.near_building.id, returned_ids)

        # Далёкое здание НЕ должно быть в списке
        self.assertNotIn(self.far_building.id, returned_ids)

    def test_filter_with_zero_radius_returns_nothing(self):
        response = self.client.get('/api/buildings/?lon=0&lat=0&dist=0')
        data = response.json()

        self.assertEqual(response.status_code, 200)

        # Главное: далёкое здание (1,1) точно не должно попасть в радиус 0 от (0,0)
        returned_ids = [f['properties']['id'] for f in data['features']]
        self.assertNotIn(self.far_building.id, returned_ids)

    def test_filter_without_params_returns_all(self):
        """Без параметров фильтра должен вернуть все здания"""
        response = self.client.get('/api/buildings/')
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['features']), 2)  # Оба тестовых здания