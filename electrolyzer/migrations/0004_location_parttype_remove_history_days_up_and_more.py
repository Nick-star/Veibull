# Generated by Django 4.2 on 2023-06-26 10:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('electrolyzer', '0003_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('building', models.CharField(max_length=50)),
                ('block', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PartType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='history',
            name='days_up',
        ),
        migrations.AddField(
            model_name='history',
            name='months_up',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electrolyzer.location')),
                ('part_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electrolyzer.parttype')),
            ],
        ),
        migrations.AddField(
            model_name='history',
            name='part',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='electrolyzer.part'),
        ),
        migrations.AlterField(
            model_name='electrolyzer',
            name='building',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electrolyzer.location'),
        ),
        migrations.AlterField(
            model_name='electrolyzer',
            name='electrolyzer_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electrolyzer.parttype'),
        ),
        migrations.DeleteModel(
            name='Building',
        ),
        migrations.DeleteModel(
            name='ElectrolyzerType',
        ),
    ]