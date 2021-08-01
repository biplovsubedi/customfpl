from utils.jsondata import JsonData
from utils.gameweek_service import GameweekService
from fplservice.models import Gameweek
from django.core.exceptions import ObjectDoesNotExist
import antifpl.models as anti
from utils.gw_picks import GameweekPicks, Picks, Squad
from operator import itemgetter
from django.db import transaction
from django.utils import timezone
from django.conf import settings as st
import datetime

CAPTAIN_PENALTY = 15
INACTIVE_PLAYER_PENALTY = 9
BANK_PENALTY = 25


class Antifpl(JsonData):
    """Main class to perform all antifpl related processing

    The idea is that the get_data method of this class is called
    by an antifpl view to fetch all related data.


    Also try to implement caching to serve requests quickly

    """

    def __init__(self):
        # self.storage_file_path = f"{self.storage_root}/antifpl_data/{gw}.json"
        self.storage_file_path = f"{self.storage_root}/antifpl_data/live.json"
        self.gameweek_service = GameweekService()
        self.gw = self.gameweek_service.find_current_gw()

    def get_last_gw_points(self):
        """Returns a dict of team_id : points of last gw"""
        return {
            p.manager.team_id: p.total
            for p in anti.PointsTable.objects.filter(gw=self.gw - 1)
        }

    def get_last_gw_rank(self):
        """Returns a dict of team_id : rank of last gw"""
        return {
            p.manager.team_id: p.rank
            for p in anti.PointsTable.objects.filter(gw=self.gw - 1)
        }

    @staticmethod
    def get_inactive_players(picks, player_minutes):
        """Find the number of inactive players for a certian manager
        Loops in the manager picks (players) in a GW and checks if
        the player_minutes
        Find the count of players who are playing -> 'multiplier' != 0
        and minutes != 0.

        Args:
            picks (Picks): Contains the information on the manager's GW picks
            player_minutes (dict): Contains the minutes played by all
                players in that GW

        Returns:
            int: Number of starting XI players who didn't play in that GW
        """
        active_cnt = 0
        total_players = 15 if picks.active_chip == "bboost" else 11

        for p in picks.squad.team:
            if p["multiplier"] != 0 and player_minutes[p["element"]] != 0:
                active_cnt += 1
        return abs(total_players - active_cnt)

    @staticmethod
    def get_captain_penalty(picks, all_players_mins):
        """Calculate the penalties for inactive captain/vc

        C/VC penalty -> C/VC failed to play (+15 Points)

        """

        captain, vc = picks.squad.get_captains()

        return (
            CAPTAIN_PENALTY
            if (all_players_mins[captain] == 0 and all_players_mins[vc] == 0)
            else 0
        )

    @staticmethod
    def get_bank_penalty(itb):
        """Return bank penalty for a user

        Bank Penalty: More than 3.0 in the bank
        Penalty of 25 points
        """
        return BANK_PENALTY if itb > 3.0 else 0

    def complete_gameweek(self):
        """This function is called when a gameweek is completed and all
        the gameweek related info needs to be saved
        """
        # Delete cached json to get new data
        self.gameweek_picks.delete_json_data()

        self.gameweek_picks = GameweekPicks(gw=self.gw)
        all_managers_picks = self.gameweek_picks.get_gw_picks()

        # Get the points scored by all the players
        all_players_points = self.gameweek_service.get_players_points()
        all_players_mins = self.gameweek_service.get_players_minutes()

        last_gw_points = self.get_last_gw_points()

        # Finalize the points scored by all the players
        final_gw_total = []
        for team_id, gw_picks in all_managers_picks.items():
            picks = Picks(gw_picks)
            try:
                last_gw_points = last_gw_points[team_id]
            except KeyError:
                print("Raise Error")
                last_gw_points = 0

            inactive_players = self.__class__.get_inactive_players(
                picks, all_players_mins
            )
            inactive_players_pens = inactive_players * INACTIVE_PLAYER_PENALTY
            captain_penalty = self.__class__.get_captain_penalty(
                picks, all_players_mins
            )
            transfer_hits = picks.transfers_cost
            bank_penalty = self.__class__.get_bank_penalty(picks.bank)
            gw_points = (
                picks.points
                + bank_penalty
                + transfer_hits
                + captain_penalty
                + inactive_players_pens
            )
            total = gw_points + last_gw_points

            final_gw_total.append(
                {
                    "team_id": team_id,
                    "site_points": picks.points,
                    "cvc_pens": captain_penalty,
                    "inactive_players": inactive_players,
                    "inactive_players_pens": inactive_players_pens,
                    "gw_points": gw_points,
                    "total": total,
                }
            )

        sorted_final_gw_total = sorted(final_gw_total, key=itemgetter("total"))
        for i, item in enumerate(sorted_final_gw_total):
            item["rank"] = i + 1

        # Save this data to the database
        with transaction.atomic():
            for points in sorted_final_gw_total:
                team_id = points["team_id"]
                del points["team_id"]
                try:
                    anti.PointsTable.objects.get(
                        manager=anti.Manager.objects.get(team_id=team_id), gw=self.gw
                    ).update(**points)
                except ObjectDoesNotExist as e:
                    print(f"Raise Error - {e}")
            Gameweek.objects.get(id=self.gw).update(last_updated=timezone.now())

    @staticmethod
    def calculate_live_points(squad, all_players_points: dict):
        return sum(
            [
                player["multiplier"] * all_players_points[player["element"]]
                for player in squad.team
            ]
        )

    def update_gameweek(self):
        """This function is called when a gameweek is live and all
        the gameweek related info needs to be updated

        This includes updating the players points
        by calculating live site points.

        Get the current points of all football players,
        for a team, sum the total points of each active
        player in the team factored by their multiplier
        """
        self.gameweek_picks = GameweekPicks(gw=self.gw)
        all_managers_picks = self.gameweek_picks.get_gw_picks()

        # Get the points scored by all the players
        all_players_points = self.gameweek_service.get_players_points()

        last_gw_points = self.get_last_gw_points()

        # Finalize the points scored by all the players
        final_gw_total = []
        for team_id, gw_picks in all_managers_picks.items():
            picks = Picks(gw_picks)
            try:
                last_gw_points = last_gw_points[team_id]
            except KeyError:
                print(f"Raise Error _ No last gw points {team_id} ")
                last_gw_points = 0

            transfer_hits = picks.transfers_cost
            bank_penalty = self.__class__.get_bank_penalty(picks.bank)
            live_points = self.__class__.calculate_live_points(
                picks.squad, all_players_points
            )
            gw_points = live_points + bank_penalty + transfer_hits
            total = gw_points + last_gw_points

            final_gw_total.append(
                {
                    "team_id": team_id,
                    "site_points": live_points,
                    "gw_points": gw_points,
                    "total": total,
                }
            )

        sorted_final_gw_total = sorted(final_gw_total, key=itemgetter("total"))
        for i, item in enumerate(sorted_final_gw_total):
            item["rank"] = i + 1

        # Save this data to the database
        with transaction.atomic():
            for points in sorted_final_gw_total:
                team_id = points["team_id"]
                del points["team_id"]
                try:
                    anti.PointsTable.objects.get(
                        manager=anti.Manager.objects.get(team_id=team_id), gw=self.gw
                    ).update(**points)
                except ObjectDoesNotExist:
                    print("Raise Error")
            Gameweek.objects.get(id=self.gw).update(last_updated=timezone.now())

    def start_gameweek(self):
        """This function is called when a new gameweek starts and all the

        gameweek related information in the pointstable needs to be created
        """
        # Delete cached json to get new data
        self.gameweek_picks.delete_json_data()

        self.gameweek_picks = GameweekPicks(gw=self.gw)
        all_managers_picks = self.gameweek_picks.get_gw_picks()

        last_gw_points = self.get_last_gw_points()

        new_gw_list = []
        for team_id, gw_picks in all_managers_picks.items():
            picks = Picks(gw_picks)
            try:
                last_gw_points = last_gw_points[team_id]
            except KeyError:
                print("Raise Error")
                last_gw_points = 0
            try:
                last_gw_rank = last_gw_rank[team_id]
            except KeyError:
                print("Raise Error")
                last_gw_rank = -1

            transfer_hits = picks.transfers_cost
            bank_penalty = get_bank_penalty(picks.bank)
            gw_points = picks.points + bank_penalty + transfer_hits
            total = gw_points + last_gw_points

            new_gw_list.append(
                {
                    "team_id": team_id,
                    "itb": picks.bank,
                    "transfers": picks.transfers,
                    "transfers_hits": picks.transfers_cost,
                    "chip": picks.active_chip,
                    "last_gw": last_gw_points,
                    "site_points": picks.points,
                    "gw_points": gw_points,
                    "total": total,
                }
            )

        # Save this data to the database
        with transaction.atomic():
            for item in new_gw_list:
                team_id = item["team_id"]
                try:
                    anti.PointsTable.objects.create(
                        manager=anti.Manager.objects.get(team_id=team_id),
                        gw=self.gw,
                        itb=item["itb"],
                        transfers=item["transfers"],
                        transfers_hits=item["transfers_hits"],
                        chip=item["chip"],
                        chiplast_gw=item["chiplast_gw"],
                        site_points=item["site_points"],
                        gw_points=item["gw_points"],
                        total=item["total"],
                    )
                except:
                    print("Raise Error")
            Gameweek.objects.get(id=self.gw).update(last_updated=timezone.now())

    def get_data(self):

        try:
            self.gameweek = Gameweek.objects.get(id=self.gw)
        except ObjectDoesNotExist:
            print(f"Raise Error - get_data - {self.gw}")

        # Find if the gameweek has been completed (From the database)
        # If yes, simply return the data
        if self.gameweek.completed:
            return anti.PointsTable.objects.filter(gw=self.gw)

        # Check if the GW has started or not
        # If not start this gw
        # We can check this by verifying if this gw is current or not
        if not self.gameweek.is_current:
            # This GW needs to start
            self.start_gameweek()
            with transaction.atomic():
                Gameweek.objects.get(id=self.gw).update(is_current=True)
                Gameweek.objects.get(id=self.gw - 1).update(is_current=False)
            return anti.PointsTable.objects.filter(gw=self.gw)

        # At this stage, it is current gw, but not completed
        # check if the gameweek has been completed (in fantasypl api)
        # If yes, save all the gw related info
        if self.gameweek_service.is_gw_completed():

            self.complete_gameweek()
            return anti.PointsTable.objects.filter(gw=self.gw)

        # At this stage, the gw is live and needs to update with recent data
        # First check when was the GW last updated,
        # If it is more than st.MAX_REFRESH_MINS then refresh data
        if timezone.now() > self.gameweek.last_updated + datetime.timedelta(
            st.MAX_REFRESH_MINS
        ):
            self.update_gameweek()

        return anti.PointsTable.objects.filter(gw=self.gw)
