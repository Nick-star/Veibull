from datetime import date

from django.db import models


class ElectrolyzerType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Electrolyzer(models.Model):
    number = models.IntegerField()
    launch_date = models.DateField()
    failure_date = models.DateField(blank=True, null=True)
    days_up = models.IntegerField(blank=True, null=True)
    electrolyzer_type = models.ForeignKey(ElectrolyzerType, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)

    @property
    def days_to_today(self) -> int:
        return self.days_to_date(date.today())

    def days_to_date(self, d: date) -> int:
        """
        Вычисляет d - self.launch_date в днях.
        :param d:
        :return:
        """
        return (d - self.launch_date).days

    def __str__(self):
        return f'Part(number={self.number}, launch_date={self.launch_date}, ' \
               f'failure_date={self.failure_date}, days_up={self.days_up}, ' \
               f'electrolyzer_type={self.electrolyzer_type}, building={self.building})'
