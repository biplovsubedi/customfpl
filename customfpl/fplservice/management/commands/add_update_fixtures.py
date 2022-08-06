""" 
Usage: python manage.py add_update_fixtures --settings=customfpl.settings.prod
"""

from django.core.management.base import BaseCommand, CommandError
import json

from django.conf import settings as st
from django.utils import timezone
from fplservice.models import Gameweek

from utils.request_service import request_data_from_url
from utils.url_endpoints import URL_BOOTSTRAP_STATIC
from os.path import join

FIXTURES_JSON_PATH = "jsondata/fixtures.json"

DEADLINE_OFFSET_SECS = 4000
TWO_WEEKS_SECS = 20160


def get_fixtures_list_local():
    try:
        with open(FIXTURES_JSON_PATH, "r") as f:
            return json.loads(f.read())
    except Exception:
        return None

def save_fixtures(data):
    with open(FIXTURES_JSON_PATH, "w") as f:
        f.write(json.dumps(data))


def get_fixtures_list():
    if (fixtures := get_fixtures_list_local()):
        return fixtures
    print("could not get fixtures - getting from fpl api")
    bootstrap_static_data = request_data_from_url(URL_BOOTSTRAP_STATIC)
    try:
        fixtures =  bootstrap_static_data["events"]
        save_fixtures(fixtures)
        return fixtures
    except Exception as e:
        print(f"Could not get fixtures info - {e}")
    

class Command(BaseCommand):
    help = "Add new users/managers/entries to anti fpl league"

    def handle(self, *args, **options):

        fixture_list = get_fixtures_list()
        curr_start_time = int(timezone.now().timestamp())
        gameweek_objects = [
            Gameweek(
                id=fixture["id"],
                name=fixture["name"],
                start_time=fixture["deadline_time_epoch"] + DEADLINE_OFFSET_SECS,
                end_time=None,
                completed=False,
                is_current=False,
            )
            for fixture in fixture_list
        ]

        # Correct end time by getting from next entry
        for i in range(0, len(gameweek_objects) - 1):
            gameweek_objects[i].end_time = gameweek_objects[i + 1].start_time

        # Allowing last fixture to complete in 2 weeks from deadline
        gameweek_objects[-1].end_time = gameweek_objects[-1].start_time + TWO_WEEKS_SECS

        Gameweek.objects.bulk_create(gameweek_objects)
        print(f"Created Gameweek objects")
