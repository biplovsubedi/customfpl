# Generated by Django 3.2.5 on 2021-08-09 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('antifpl', '0003_footballerperformanceanti'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pointstable',
            unique_together={('manager', 'gw')},
        ),
    ]
