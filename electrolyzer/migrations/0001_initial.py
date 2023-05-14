# Generated by Django 4.2 on 2023-05-14 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrolyzerType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Electrolyzer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('launch_date', models.DateField()),
                ('failure_date', models.DateField(blank=True)),
                ('days_up', models.IntegerField(blank=True)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electrolyzer.building')),
                ('electrolyzer_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electrolyzer.electrolyzertype')),
            ],
        ),
    ]
