# Generated by Django 3.2.5 on 2021-08-14 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('antifpl', '0007_auto_20210814_0218'),
    ]

    operations = [
        migrations.AddField(
            model_name='footballerperformanceanti',
            name='form_5_gw',
            field=models.FloatField(default=0, verbose_name='Form (5 GW)'),
        ),
        migrations.AddField(
            model_name='footballerperformanceanti',
            name='form_season',
            field=models.FloatField(default=0, verbose_name='Form (Season)'),
        ),
        migrations.AddField(
            model_name='footballerperformanceanti',
            name='points_per_mil_5_gw',
            field=models.FloatField(default=0, verbose_name='Points Per Million (5 GW)'),
        ),
        migrations.AddField(
            model_name='footballerperformanceanti',
            name='points_per_mil_season',
            field=models.FloatField(default=0, verbose_name='Points Per Million (Season)'),
        ),
    ]