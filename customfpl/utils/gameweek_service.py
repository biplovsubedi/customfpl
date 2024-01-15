import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from fplservice.models import Gameweek

from utils.request_service import request_data_from_url
from utils.url_endpoints import URL_BOOTSTRAP_STATIC, URL_GW_LIVE


from django.conf import settings as st


class GameweekService:
    def __init__(self):
        self.current_gw = None
        self.players_data = None
        self.players_points = None
        self.players_stats = None
        self.players_minutes = None
        self.live_request_time = timezone.now() - datetime.timedelta(
            minutes=(st.MAX_REFRESH_MINS + 1)
            # to make sure first request is always processed
        )

    def find_current_gw(self):
        """Find the gameweek corresponding to the request time
        Uses gameweek fixtures file to match current time to the gw
        {
            "id": 3,
            "name": "Gameweek 3",
            "deadline_time": "2020-09-26T10:00:00Z",
            "deadline_time_epoch": 1601114400
        }
        Smallest unit in epoch time is seconds.

        Returns:
            int: Gamweeek corresponding to the request time, 0 if invalid
        """
        # return 32
        # # with open(fixture_date_file, 'r') as file:
        # #     fixtures = file.read()
        # # fixture_d = json.loads(fixtures)
        # epoch_time = calendar.timegm(time.gmtime())

        # # 4500s / 75min after the GW deadline
        # # GW deadline is roughly 90min / 5400s before first fixture
        # for f in fixtures:
        #     if f['deadline_time_epoch'] + 4000 > epoch_time:
        #         return f['id'] - 1
        # return 0
        if self.current_gw:
            return self.current_gw
        current_time = timezone.now().timestamp()
        item = Gameweek.objects.filter(
            start_time__lt=current_time, end_time__gt=current_time
        )
        if item.count() == 0:
            print("Raise Error - no gw found")
            return 38
        return item[0].id

    def is_gw_completed(self, gw=None):
        """Checks if a certain gameweek has been completed or not
        bootstrap_static contains the GW information in key 'events'
        Each gameweek has 2 parameters 'finished' and 'data_checked'.
        GW is considered completed after both these parameters are set to True

        Args:
            gw (int): gameweek no

        Returns:
            bool: True if Completed, False Otherwise
        """
        if not gw:
            gw = self.find_current_gw()

        bootstrap_static = request_data_from_url(URL_BOOTSTRAP_STATIC)
        try:
            events = bootstrap_static["events"]
        except:
            return False

        for ev in events:
            if ev["id"] == int(gw):
                return ev["finished"] and ev["data_checked"]
        return False
    
    def is_gw_active(self, gw=None):
        """Checks if the gameweek is active or not"""
        if not gw:
            gw = self.find_current_gw()
        
        return Gameweek.objects.get(id=gw).active_gameweek

    def get_gw_players_data(self, gw=None):
        """Get data of the players in a given gameweek
        Used to find players' points, minutes, etc

        This is expected to be updated very frequently
        Will not be saved/cached in the json db

        """
        if not gw:
            gw = self.find_current_gw()

        # Don't return stale data that is MAX_REFRESH_MINS+ old
        if (
            self.players_data
            and timezone.now() - datetime.timedelta(st.MAX_REFRESH_MINS)
            < self.live_request_time
        ):
            return self.players_data

        _gw_players_data = request_data_from_url(URL_GW_LIVE.format(gw=gw))
        try:
            self.players_data = _gw_players_data["elements"]
            self.live_request_time = timezone.now()
        except KeyError:
            print("Raise Error")
            return {}
        return self.players_data

    def get_players_minutes(self, gw=None):
        """Extract the playing minutes for all players in a gw
        Each player has a ton of stats in each GW, Only one that we need
        for processing is the minutes. So we filter out unnecessary
        information
        GW minutes is used to compute inactive players penalties

        Dictionary converstion is done to save lookup time O(N) -> O(1)

        Args:
            gw (int): gameweek

        Returns:
            dict: contains player's id(key) and mintues(val)
        """
        if self.players_minutes:
            return self.players_minutes

        players = self.get_gw_players_data(gw)

        _players_minutes = {p["id"]: p["stats"]["minutes"] for p in players}
        self.players_minutes = _players_minutes
        return _players_minutes

    def get_players_points(self, gw=None, only_played=False):
        """Extract the playing points for all players in a gw
        Each player has a ton of stats in each GW, Only one that we need
        for processing is the points. So we filter out unnecessary
        information
        GW points is used to compute inactive players penalties

        Dictionary converstion is done to save lookup time O(N) -> O(1)

        Args:
            gw (int): gameweek
            only_played(bool) : don't add players that have 0 mins
                used for dream team

        Returns:
            dict: contains player's id(key) and mintues(val)
        """
        if self.players_points:
            return self.players_points

        players = self.get_gw_players_data(gw)
        _players_points = {}
        for p in players:
            if only_played and p["stats"]["minutes"] == 0:
                continue
            _players_points[p["id"]] = p["stats"]["total_points"]
        self.players_points = _players_points
        return _players_points

    def get_players_stats(self, gw=None, only_played=False):
        """Extract the points and playing minutes for all players in a gw
        Args:
            gw (int): gameweek
            only_played(bool) : don't add players that have 0 mins
                used for dream team

        Returns:
            dict: contains player's id(key) and mintues(val)
        """
        if self.players_stats:
            return self.players_stats

        players = self.get_gw_players_data()
        _players_stats = {}
        for p in players:
            if only_played and p["stats"]["minutes"] == 0:
                continue
            _players_stats[p["id"]] = {
                "points": p["stats"]["total_points"],
                "minutes": p["stats"]["minutes"],
            }
        self.players_points = _players_stats
        return _players_stats
