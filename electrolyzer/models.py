from datetime import date

from django.core.exceptions import ValidationError
from django.db import models


class PartType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Factory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=100)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)

    def clean(self):
        if self.factory.building_set.exclude(pk=self.pk).filter(name__exact=self.name).exists():
            raise ValidationError('Уже есть такое здание.')

    def __str__(self):
        return f'{self.factory} {self.name}'


class Part(models.Model):
    number = models.IntegerField(verbose_name='номер')
    avg_days = models.FloatField(blank=True, null=True, editable=False)
    part_type = models.ForeignKey(PartType, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('number', 'part_type', 'building')

    def __str__(self):
        return f"{self.part_type} #{self.number}"


class History(models.Model):
    launch_date = models.DateField(verbose_name='дата запуска')
    failure_date = models.DateField(verbose_name='дата поломки', blank=True, null=True)
    days = models.IntegerField(null=True, editable=False)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)

    @property
    def days_to_today(self) -> int:
        return (date.today() - self.launch_date).days

    def save(self, *args, **kwargs):
        self.days = (self.failure_date - self.launch_date).days if self.failure_date else None
        super().save(*args, **kwargs)
        results = self.part.history_set.exclude(days__isnull=True).aggregate(avg_days=models.Avg('days'))
        self.part.avg_days = results['avg_days']
        self.part.save()

    def clean(self):
        if self.failure_date:
            if self.failure_date < self.launch_date:
                raise ValidationError("Дата поломки не должна быть до даты запуска.")

    def __str__(self):
        return f'{self.part} {self.launch_date} {self.failure_date} {self.days}'


class Electrolyzer(models.Model):
    number = models.IntegerField()
    launch_date = models.DateField()
    failure_date = models.DateField(blank=True, null=True)
    days_up = models.IntegerField(blank=True, null=True)
    electrolyzer_type = models.ForeignKey(PartType, on_delete=models.CASCADE)
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
