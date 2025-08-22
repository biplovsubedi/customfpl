""" 
Usage: python manage.py add_new_footballers --settings=customfpl.settings.prod
"""

from django.core.management.base import BaseCommand, CommandError
import json

from django.conf import settings as st
from django.utils import timezone

from utils.request_service import request_data_from_url
from utils.url_endpoints import URL_BOOTSTRAP_STATIC

from django.db import transaction
from fplservice.models import Footballer, Position, TeamMeta
from django.core.exceptions import ObjectDoesNotExist


def get_footballers_list():

    bootstrap_static_data = request_data_from_url(URL_BOOTSTRAP_STATIC)
    try:
        return bootstrap_static_data["elements"]
    except KeyError:
        print("Error getting players data")
        return []


def add_update_footballers_meta():
    added = 0
    updated = 0
    footballer_list = get_footballers_list()
    with transaction.atomic():
        for footballer in footballer_list:
            try:
                existing_footballer = Footballer.objects.get(id=footballer["id"])
                Footballer.objects.filter(id=footballer["id"]).update(
                    cost=footballer["now_cost"],
                    assists=footballer["assists"],
                    goals_conceded=footballer["goals_conceded"],
                    clean_sheets=footballer["clean_sheets"],
                    goals_scored=footballer["goals_scored"],
                    yellow_cards=footballer["yellow_cards"],
                    red_cards=footballer["red_cards"],
                )
                updated += 1
            except ObjectDoesNotExist:
                try:
                    Footballer.objects.create(
                        id=footballer["id"],
                        name=footballer["web_name"],
                        team=TeamMeta.objects.get(id=footballer["team"]),
                        position=Position.objects.get(id=footballer["element_type"]),
                        cost=footballer["now_cost"],
                        assists=footballer["assists"],
                        goals_conceded=footballer["goals_conceded"],
                        clean_sheets=footballer["clean_sheets"],
                        goals_scored=footballer["goals_scored"],
                        yellow_cards=footballer["yellow_cards"],
                        red_cards=footballer["red_cards"],
                    )
                    added += 1
                except (TeamMeta.DoesNotExist, Position.DoesNotExist) as e:
                    print(f"Error creating footballer {footballer['web_name']}: {e}")
            except Exception as e:
                print(f"Unexpected error processing footballer {footballer['web_name']}: {e}")
    print(f"Total Footballers added : {added} , updated: {updated}")


class Command(BaseCommand):
    help = "Add new footballers to the Database"

    def handle(self, *args, **options):
        add_update_footballers_meta()
