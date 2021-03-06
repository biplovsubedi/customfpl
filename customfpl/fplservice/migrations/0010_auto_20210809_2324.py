# Generated by Django 3.2.5 on 2021-08-09 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fplservice', '0009_footballer_position'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='footballer',
            options={'ordering': ('-cost',), 'verbose_name': 'Footballer', 'verbose_name_plural': 'Footballers'},
        ),
        migrations.AddField(
            model_name='position',
            name='squad_max_play',
            field=models.IntegerField(default=1, verbose_name='Max Playing'),
        ),
        migrations.AddField(
            model_name='position',
            name='squad_max_select',
            field=models.IntegerField(default=1, verbose_name='Max in Squad'),
        ),
        migrations.AddField(
            model_name='position',
            name='squad_min_play',
            field=models.IntegerField(default=1, verbose_name='Min Playing'),
        ),
    ]
