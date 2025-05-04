from django.db import models

    

class Weather(models.Model):
    date = models.DateField()
    location = models.CharField(max_length=100)
    temp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dwpt = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rhum = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wpgt = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tsun = models.IntegerField(null=True, blank=True)
    wdir = models.IntegerField(null=True, blank=True)
    coco = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weather = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'weather_data'
        ordering = ["location", "date"]

    def __str__(self):
        return f'{self.date} - {self.location}: {self.weather}'