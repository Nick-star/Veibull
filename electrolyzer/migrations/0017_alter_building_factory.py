# Generated by Django 4.2 on 2023-06-27 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('electrolyzer', '0016_alter_building_factory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='factory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electrolyzer.factory'),
        ),
    ]
