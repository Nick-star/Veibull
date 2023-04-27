from django.db import models


class Electrolyzer(models.Model):
    electrolyzer_number = models.IntegerField()
    release_date = models.DateField()
    shutdown_date = models.DateField()
    shutdown_life = models.FloatField()
    average_lifetime = models.FloatField()

    def __str__(self):
        return f"Electrolyzer {self.electrolyzer_number}"