# Generated by Django 3.2.5 on 2021-08-12 12:39

import auto_prefetch
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fplservice', '0010_auto_20210809_2324'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='position',
            options={'verbose_name': 'Position'},
        ),
        migrations.RemoveField(
            model_name='footballerperformance',
            name='total_selection',
        ),
        migrations.AddField(
            model_name='footballerperformance',
            name='captains',
            field=models.IntegerField(default=0, verbose_name='Captaincy'),
        ),
        migrations.AddField(
            model_name='footballerperformance',
            name='cvc',
            field=models.IntegerField(default=0, verbose_name='Captain/Vice Captain'),
        ),
        migrations.AddField(
            model_name='footballerperformance',
            name='squad_xv',
            field=models.IntegerField(default=0, verbose_name='Squad Selection'),
        ),
        migrations.AddField(
            model_name='footballerperformance',
            name='starting_xi',
            field=models.IntegerField(default=0, verbose_name='Starting XI Selection'),
        ),
        migrations.AlterField(
            model_name='footballerperformance',
            name='gw',
            field=auto_prefetch.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fplservice.gameweek', verbose_name='Gameweek'),
        ),
    ]
