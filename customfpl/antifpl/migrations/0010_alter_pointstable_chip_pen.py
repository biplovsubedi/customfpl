# Generated by Django 3.2.5 on 2022-09-16 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('antifpl', '0009_pointstable_chip_pen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointstable',
            name='chip_pen',
            field=models.IntegerField(blank=True, null=True, verbose_name='Chip Penalty'),
        ),
    ]
