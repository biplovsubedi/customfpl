"""This module/command is used to add any new entries to the anti fpl 

It checks the League standings ? page_new_entries url to find any new entries in the gw.

It tries to add these new entries to the game

Usage: python manage.py add_new_entries_to_anti --settings=customfpl.settings.prod

"""

from django.core.management.base import BaseCommand, CommandError
import antifpl.models as anti
from utils.url_endpoints import (
    URL_NEW_ENTRIES_ANTI,
    LEAGUE_CODE_ANTI,
    URL_STANDINGS_BASE_ANTI,
)
from utils.request_service import request_data_from_url


class AddNewAntiPlayers:
    def __init__(self):
        pass

    @staticmethod
    def get_all_new_entries():
        all_new_entries = []
        page_no = 1
        while True:
            request_url = f"{URL_NEW_ENTRIES_ANTI}{page_no}"
            print(request_url)

            response_data = request_data_from_url(request_url)

            all_new_entries.extend(response_data["new_entries"]["results"])

            if response_data["new_entries"]["has_next"]:
                page_no += 1
            else:
                return all_new_entries

    @staticmethod
    def get_all_old_entries():
        all_old_entries = []
        page_no = 1
        while True:
            request_url = f"{URL_STANDINGS_BASE_ANTI}{page_no}"
            print(request_url)

            response_data = request_data_from_url(request_url)

            all_old_entries.extend(response_data["standings"]["results"])

            if response_data["standings"]["has_next"]:
                page_no += 1
            else:
                return all_old_entries

    def process(self):

        new_entries = self.__class__.get_all_new_entries()
        old_entries = self.__class__.get_all_old_entries()

        added_entries_counter = 0
        for entry in new_entries + old_entries:
            try:
                anti.Manager.objects.create(
                    team_id=entry["entry"],
                    team_name=entry["entry_name"],
                    manager_id=entry["entry"],  # TODO: Fix this
                    manager_name=f"{entry['player_first_name']} {entry['player_last_name']}",
                )
                added_entries_counter += 1
            except:
                print(f"Manager Exists - {entry}")
        return added_entries_counter


class Command(BaseCommand):
    help = "Add new users/managers/entries to anti fpl league"

    def handle(self, *args, **options):

        add_new_anti_players = AddNewAntiPlayers()
        counter = add_new_anti_players.process()
        print(f"Total Managers added: {counter}")
