# Generated by Django 3.2.5 on 2021-08-01 11:42

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('fplservice', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMeta',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='Id')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='Name')),
                ('short_name', models.CharField(max_length=3, unique=True, verbose_name='Short Name')),
                ('code', models.IntegerField(unique=True, verbose_name='Team Code')),
            ],
            options={
                'verbose_name': 'TeamMeta',
                'verbose_name_plural': 'TeamMetas',
            },
        ),
        migrations.AlterModelOptions(
            name='gameweek',
            options={'verbose_name': 'Gameweek', 'verbose_name_plural': 'Gameweeks'},
        ),
        migrations.RemoveField(
            model_name='gameweek',
            name='deadline_time',
        ),
        migrations.RemoveField(
            model_name='gameweek',
            name='deadline_time_epoch',
        ),
        migrations.AddField(
            model_name='gameweek',
            name='completed',
            field=models.BooleanField(default=False, verbose_name='GW Completed'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gameweek',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 1, 11, 42, 17, 528784, tzinfo=utc), verbose_name='End Time'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gameweek',
            name='is_current',
            field=models.BooleanField(default=False, verbose_name='Is Current GW'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gameweek',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Last Updated Time'),
        ),
        migrations.AddField(
            model_name='gameweek',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 1, 11, 42, 35, 619439, tzinfo=utc), verbose_name='Start Time'),
            preserve_default=False,
        ),
    ]
