from django.db import models

from dotenv import load_dotenv
from decouple import config
load_dotenv()


class Weather(models.Model):
    province = models.CharField(max_length=100, verbose_name="Province")
    time = models.DateTimeField(verbose_name="Time")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Temperature")
    temp_max = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Max Temperature")
    temp_min = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Min Temperature")
    precipitation = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Precipitation")
    windspeed_max = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Max Windspeed")
    uv_index_max = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Max UV Index")
    sunshine_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Sunshine Hours")
    sundown_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Sundown Hours")
    weather_code = models.IntegerField(verbose_name="Weather Code")

    class Meta:
        managed = False
        db_table = config("WEATHER_DATA_TABLE_NAME", default="weather_data")
        ordering = ["province", "time"]

    def __str__(self):
        return f'{self.province} - {self.time}: {self.temperature}'