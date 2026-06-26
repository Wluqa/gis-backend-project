import json
from rest_framework import serializers
from .models import Building


class BuildingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Building
        # Поля, которые будут участвовать в сериализации
        fields = ['id', 'geom', 'address']

    # === Валидатор геометрии для DRF ===
    def validate_geom(self, value):
        """
        Проверка валидности геометрии перед сохранением
        Вызывается автоматически при валидации данных из запроса
        """
        if value is None:
            raise serializers.ValidationError("Поле геометрии обязательно.")

        # Проверяем, что геометрия валидна (нет самопересечений и т.п.)
        if not value.valid:
            raise serializers.ValidationError(
                "Геометрия не проходит проверку валидности (ST_IsValid). "
                "Проверьте, что полигон замкнут и не имеет самопересечений."
            )
        return value

    # === Преобразование в GeoJSON Feature ===
    def to_representation(self, instance):
        """
        Переопределяем вывод: возвращаем GeoJSON Feature вместо обычного JSON
        Соответствует RFC 7946 (спецификация GeoJSON)
        """
        # Сначала получаем стандартное представление
        rep = super().to_representation(instance)

        # Парсим геометрию из формата Django в GeoJSON-словарь
        geom_dict = json.loads(instance.geom.json)

        # Формируем объект типа Feature по спецификации GeoJSON
        return {
            "type": "Feature",
            "geometry": geom_dict,
            "properties": {
                "id": rep["id"],
                "address": rep["address"]
            }
        }

    # === Преобразование из GeoJSON при создании/обновлении ===
    def to_internal_value(self, data):
        """
        Обрабатывает входящие данные: принимает GeoJSON Feature и извлекает геометрию
        """
        # Если пришёл объект типа Feature — извлекаем geometry и properties
        if isinstance(data, dict) and data.get("type") == "Feature":
            geometry = data.get("geometry")
            properties = data.get("properties", {})

            # Собираем данные в формат, понятный Django-модели
            data = {
                "geom": geometry,
                "address": properties.get("address"),
                "id": properties.get("id")
            }

        return super().to_internal_value(data)