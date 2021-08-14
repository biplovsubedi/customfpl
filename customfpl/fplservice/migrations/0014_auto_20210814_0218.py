# Generated by Django 3.2.5 on 2021-08-13 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fplservice', '0013_auto_20210812_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='footballerperformance',
            name='minutes',
            field=models.PositiveIntegerField(null=True, verbose_name='GW Minutes'),
        ),
        migrations.AlterField(
            model_name='footballerperformance',
            name='points',
            field=models.IntegerField(null=True, verbose_name='GW Points'),
        ),
    ]
