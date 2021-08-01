from antifpl.models import Manager
from utils.request_service import request_data_from_url
from utils.url_endpoints import URL_GW_PICKS

from .jsondata import JsonData
from dataclasses import dataclass


@dataclass
class Squad:
    """
    This dataclass is used to represent the squad of each manager

    class members:
        captain
        vice_captain
        team : list of tuple(element_id, multiplier)

    'picks' : [
            {
                'element' : 111,
                'position' : 1,
                'multiplier' : 1,
                'is_captain' : false,
                'is_vice_captain' : false
            },
            ...
        ]

    """

    def __init__(self, picks):
        self.captain = None
        self.vice_captain = None
        self.team = []
        try:
            for pick in picks:
                if pick["is_captain"]:
                    self.captain = pick["element"]
                if pick["is_vice_captain"]:
                    self.vice_captain = pick["element"]
                # TODO namedtuple
                team.append((pick["element"], pick["multiplier"]))
        except KeyError:
            print("Raise Exception")

    def get_captains(self):
        """Returns a tuple of (captain, vice_captain)"""
        return (self.captain, self.vice_captain)


@dataclass
class Picks:
    """
    Dataclass used to represent the gw picks for each manager

    picks = {
        'active_chip' : null,
        'automatic_subs' : [],
        'entry_history' : {
            // Event details
            'event' : gw,
            'points', 'total_points', 'rank', 'rank_sort', 'overall_rank',
            'bank', 'value',
            'event_transfers', 'event_transfers_cost',
            'points_on_bench'
        },
        'picks' : [
            {
                'element' : 111,
                'position' : 1,
                'multiplier' : 1,
                'is_captain' : false,
                'is_vice_captain' : false
            },
            ...
        ]
    }

    """

    def __init__(self, picks):
        try:
            self.active_chip = picks["active_chip"]
            self.points = picks["entry_history"]["points"]
            self.bank = picks["entry_history"]["bank"]
            self.team_value = picks["entry_history"]["value"]
            self.transfers = picks["entry_history"]["event_transfers"]
            self.transfers_cost = picks["entry_history"]["event_transfers"]
            self.squad = Squad(picks["picks"])

        except KeyError:
            print("Raise exception")


class GameweekPicks(JsonData):
    """This class is used to represent the gameweek picks of all the managers
    in a certain gameweek.

    It inherits from the JsonData class, so this class is expected to save/cache
    all the results in JSON_ROOT path for each gw pick.

    Format for each JSON:
    {
        'manager_id' : picks,
        ...
    }
    """

    def __init__(self, gw):
        self.gw = gw
        self.all_managers_id = None
        self.storage_file_path = f"{self.storage_root}/gameweek_picks/{gw}.json"
        self.gw_picks = None

    def _get_all_managers_id(self):
        if self.all_managers_id:
            return self.all_managers_id

        return [m.team_id for m in Manager.objects.all()]

    def _fetch_picks_for_all_players(self):
        """For all the players in the league, find their respective
        gameweek picks.
        This information is used to find captains/vice captains, bank/squad value,
        weekly players pick, calcualte penalties.

        Return Format:
        {
            'manager_id1' : picks,
            'manager_id2' : picks,
            ...
        }

        Args:
            gw (int): gameweek
            gw_standings (dict): list of FPL managers in the mini league

        Returns:
            dict: Contains the gw picks information for all managers
        """
        complete_gw_picks = {}
        for entry_id in self._get_all_managers_id():
            # entry_id = player['entry']
            if (
                picks := request_data_from_url(
                    URL_GW_PICKS.format(entry=entry_id, gw=gw)
                )
            ) != None:
                complete_gw_picks[entry_id] = picks

        return complete_gw_picks

    def get_gw_picks(self):

        _gw_picks = self.read_json_data()
        if _gw_picks:
            self.gw_picks = _gw_picks
            return gw_picks

        # This Gw picks isn't saved, so we need to donwload
        # and save gw picks for each manager

        self.gw_picks = self._fetch_picks_for_all_players()
        # Save complete gw teams for future access
        self.write_json_data(self.gw_picks)

        return self.gw_picks
