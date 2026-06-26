
from django.contrib.gis.db import models  # GIS-версия моделей
from django.core.exceptions import ValidationError


class Building(models.Model):

    geom = models.PolygonField(
        srid=4326,
        help_text="Полигон в системе координат WGS84 (EPSG:4326)"
    )

    address = models.CharField(
        max_length=255,
        help_text="Почтовый адрес здания"
    )

    class Meta:
        verbose_name = "Здание"
        verbose_name_plural = "Здания"
        ordering = ['address']
    def clean(self):

        super().clean()
        if self.geom and not self.geom.valid:
            raise ValidationError({
                'geom': 'Передана невалидная геометрия: '
                        'самопересечение, незамкнутый контур или неверный формат.'
            })

    def __str__(self):
        return f"Здание: {self.address}"