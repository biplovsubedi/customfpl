""" 
Usage: python manage.py add_new_teams --settings=customfpl.settings.prod
"""

from django.core.management.base import BaseCommand, CommandError

from utils.request_service import request_data_from_url
from utils.url_endpoints import URL_BOOTSTRAP_STATIC

from fplservice.models import TeamMeta
from django.core.exceptions import ObjectDoesNotExist


def get_teams_list():

    bootstrap_static_data = request_data_from_url(URL_BOOTSTRAP_STATIC)
    try:
        return bootstrap_static_data["teams"]
    except KeyError:
        print("Error getting teams data")
        return []


class Command(BaseCommand):
    help = "Add new teams to the Database"

    def handle(self, *args, **options):
        counter = 0
        team_list = get_teams_list()
        for team in team_list:
            try:
                TeamMeta.objects.get(id=team["id"])
            except ObjectDoesNotExist:
                TeamMeta.objects.create(
                    id=team["id"],
                    name=team["name"],
                    short_name=team["short_name"],
                    code=team["code"],
                )
                counter += 1
        print(f"Total teams added : {counter}")
