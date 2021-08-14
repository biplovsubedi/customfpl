from antifpl.models import Manager, PointsTable
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

""" 
Initializes anti points table for the first time 

Usage: python manage.py initialize_anti_points_table --settings=customfpl.settings.prod

"""


def intialize_gw0():

    all_managers = Manager.objects.all()
    counter = 0
    with transaction.atomic():
        for manager in all_managers:
            try:
                PointsTable.objects.get(manager=manager, gw=0)
            except ObjectDoesNotExist:
                PointsTable.objects.create(
                    manager=manager,
                    gw=0,
                    team_value=0,
                    itb=0,
                    transfers=0,
                    transfers_hits=0,
                    last_gw=0,
                    site_points=0,
                    gw_points=0,
                    rank=0,
                    last_rank=0,
                    total=0,
                )
                counter += 1
    print(f"Points table updated with gw 0 : {counter}")


class Command(BaseCommand):
    help = "Initializes anti gw 0 table with blank entries"

    def handle(self, *args, **options):

        intialize_gw0()
