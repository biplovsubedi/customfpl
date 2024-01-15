import datetime
from collections import defaultdict
from operator import itemgetter

from django.conf import settings as st
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from fplservice.management.commands.add_new_footballers import (
    add_update_footballers_meta,
)
from fplservice.models import Footballer, Gameweek
from utils.gameweek_service import GameweekService
from utils.gw_picks import GameweekPicks, Picks, Squad
from utils.jsondata import JsonData
from os.path import join
import antifpl.models as anti
from django.db.models import Avg

CAPTAIN_PENALTY = 15
INACTIVE_PLAYER_PENALTY = 9
BANK_PENALTY = 25
CHIP_PENALTY = 25


class Antifpl(JsonData):
    """Main class to perform all antifpl related processing

    The idea is that the get_data method of this class is called
    by an antifpl view to fetch all related data.


    Also try to implement caching to serve requests quickly

    """

    def __init__(self, gw=None):
        self.storage_file_path = join(
            self.storage_root, join("antifpl_data", "live.json")
        )
        self.gameweek_service = GameweekService()
        self.gw = gw or self.gameweek_service.find_current_gw()

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
            if p[1] != 0 and player_minutes[p[0]] != 0:
                # p = (element, multiplier) tuple
                active_cnt += 1
        return abs(total_players - active_cnt)

    @staticmethod
    def get_captain_penalty(picks: Picks, all_players_mins):
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
        return BANK_PENALTY if itb > 30 else 0

    def find_chip_usage_penalty(self, team_id):
        """Find chip usage penalty for each manager at the end of the season

        Each chip usage penalty is +25 points, failure to use, bbost, 3xc will add this penalty

        Args:
            team_id (_type_): _description_
        """
        boost_count = anti.PointsTable.objects.filter(
            manager__team_id=team_id, chip="bboost"
        ).count()
        tc_count = anti.PointsTable.objects.filter(
            manager__team_id=team_id, chip="3xc"
        ).count()

        return (2 - boost_count - tc_count) * 25

    def complete_gameweek(self):
        """This function is called when a gameweek is completed and all
        the gameweek related info needs to be saved
        """

        self.gameweek_picks = GameweekPicks(gw=self.gw)

        # Delete cached json to get new data
        self.gameweek_picks.delete_json_data()

        all_managers_picks = self.gameweek_picks.get_gw_picks()

        # Get the points scored by all the players
        all_players_points = self.gameweek_service.get_players_points(self.gw)
        all_players_mins = self.gameweek_service.get_players_minutes(self.gw)
        print(f"current gw {self.gw}")

        last_gw_points_dict = self.get_last_gw_points()
        
        is_gw_active = self.gameweek_service.is_gw_active(self.gw)

        # Finalize the points scored by all the players
        final_gw_total = []
        for team_id, gw_picks in all_managers_picks.items():
            team_id = int(team_id)
            picks = Picks(gw_picks)
            try:
                last_gw_points = last_gw_points_dict[team_id]
            except KeyError:
                print(f"Raise Error - No points last gw {team_id}")
                last_gw_points = 0

            inactive_players = self.__class__.get_inactive_players(
                picks, all_players_mins
            )
            inactive_players_pens = inactive_players * INACTIVE_PLAYER_PENALTY
            captain_penalty = self.__class__.get_captain_penalty(
                picks, all_players_mins
            )
            # add 25 to captain penalty if captain penalty in triple gw
            if picks.active_chip == "3xc" and captain_penalty == CAPTAIN_PENALTY:
                captain_penalty = CHIP_PENALTY

            transfer_hits = picks.transfers_cost
            bank_penalty = self.__class__.get_bank_penalty(picks.bank)
            if not is_gw_active:
                bank_penalty = 0
                captain_penalty = 0
                inactive_players_pens = 0
                inactive_players = 0
            gw_points = (
                picks.points
                + bank_penalty
                + transfer_hits
                + captain_penalty
                + inactive_players_pens
            )
            total = gw_points + last_gw_points
            chip_pen = 0
            if self.gw == 38:
                # Last gw so, find chip usage penalty
                chip_pen = self.find_chip_usage_penalty(team_id)
                total += chip_pen

            final_gw_total.append(
                {
                    "team_id": team_id,
                    "site_points": picks.points,
                    "cvc_pens": captain_penalty,
                    "inactive_players": inactive_players,
                    "inactive_players_pens": inactive_players_pens,
                    "chip_pen": chip_pen,
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
                    anti.PointsTable.objects.filter(
                        manager__team_id=team_id, gw=self.gw
                    ).update(**points)
                except Exception as e:
                    print(f"Raise Error - Completing gw - {e}")
            Gameweek.objects.filter(id=self.gw).update(
                last_updated=timezone.now(), completed=True
            )

    @staticmethod
    def calculate_live_points(squad, all_players_points: dict):
        # print(squad.team[0])
        return sum([player[1] * all_players_points[player[0]] for player in squad.team])

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

        last_gw_points_dict = self.get_last_gw_points()

        # Finalize the points scored by all the players
        final_gw_total = []
        for team_id, gw_picks in all_managers_picks.items():
            team_id = int(team_id)
            picks = Picks(gw_picks)
            try:
                last_gw_points = last_gw_points_dict[team_id]
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
                    anti.PointsTable.objects.filter(
                        manager__team_id=team_id, gw=self.gw
                    ).update(**points)
                except ObjectDoesNotExist:
                    print("Raise Error - couldn't update points table")
            Gameweek.objects.filter(id=self.gw).update(last_updated=timezone.now())

    def start_gameweek(self):
        """This function is called when a new gameweek starts and all the

        gameweek related information in the pointstable needs to be created
        """
        # Update footballer meta
        add_update_footballers_meta()

        self.gameweek_picks = GameweekPicks(gw=self.gw)
        self.gameweek_picks.delete_json_data()
        all_managers_picks = self.gameweek_picks.get_gw_picks()

        last_gw_points_dict = self.get_last_gw_points()
        last_gw_rank_dict = self.get_last_gw_rank()

        new_gw_list = []
        for team_id, gw_picks in all_managers_picks.items():
            team_id = int(team_id)
            picks = Picks(gw_picks)
            try:
                last_gw_points = last_gw_points_dict[team_id]
            except KeyError:
                print("Raise Error - no last gw points")
                last_gw_points = 0
            try:
                last_gw_rank = last_gw_rank_dict[team_id]
            except KeyError:
                print("Raise Error - no last gw rank")
                last_gw_rank = -1

            transfer_hits = picks.transfers_cost
            bank_penalty = self.__class__.get_bank_penalty(picks.bank)
            gw_points = picks.points + bank_penalty + transfer_hits
            total = gw_points + last_gw_points

            new_gw_list.append(
                {
                    "team_id": team_id,
                    "team_value": picks.team_value,
                    "itb": picks.bank,
                    "transfers": picks.transfers,
                    "transfers_hits": picks.transfers_cost,
                    "chip": picks.active_chip,
                    "last_gw": last_gw_points,
                    "last_rank": last_gw_rank,
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
                        team_value=item["team_value"],
                        itb=item["itb"],
                        transfers=item["transfers"],
                        transfers_hits=item["transfers_hits"],
                        chip=item["chip"],
                        last_gw=item["last_gw"],
                        rank=0,  # TODO fix this, rank can't be zero
                        last_rank=item["last_rank"],
                        site_points=item["site_points"],
                        gw_points=item["gw_points"],
                        total=item["total"],
                    )
                except Exception as e:
                    print(f"Raise Error - starting gw create new objects - {e} ")
            Gameweek.objects.filter(id=self.gw).update(last_updated=timezone.now())

    def update_gw_form_stats_footballer(self):
        """Update the form stats of all the footballers"""
        all_footballers_performance = anti.FootballerPerformanceAnti.objects.filter(
            gw__id=self.gw
        )
        for footballer_performance in all_footballers_performance:

            form_5gw = round(
                anti.FootballerPerformanceAnti.objects.filter(
                    gw__id__gt=self.gw - 5, footballer=footballer_performance.footballer
                ).aggregate(Avg("anti_points"))["anti_points__avg"],
                3,
            )
            form_season = round(
                anti.FootballerPerformanceAnti.objects.filter(
                    footballer=footballer_performance.footballer
                ).aggregate(Avg("anti_points"))["anti_points__avg"],
                3,
            )

            ppm_5gw = round(form_5gw / float(footballer_performance.footballer.cost), 3)
            ppm_season = round(
                form_season / float(footballer_performance.footballer.cost), 3
            )

            with transaction.atomic():
                footballer_performance.form_5_gw = form_5gw
                footballer_performance.form_season = form_season
                footballer_performance.price_per_mil_5_gw = ppm_5gw
                footballer_performance.price_per_mil_season = ppm_season
                footballer_performance.save()

                Footballer.objects.filter(
                    id=footballer_performance.footballer.id
                ).update(
                    form_5_gw=form_5gw,
                    form_season=form_season,
                    points_per_mil_5_gw=ppm_5gw,
                    points_per_mil_season=ppm_season,
                )

    def update_dynamic_stats_footballer(self, gw_completed=False):
        """For all the players playing in this gw,
        update the playing minutes, points, etc
        """

        # Get the playing minutes, points of each footballer and update that
        # Also update anti points if gw completed

        all_players_stats = self.gameweek_service.get_players_stats()

        break_flag = False

        with transaction.atomic():
            for footballer_id, stats in all_players_stats.items():
                footballer_id = int(footballer_id)
                anti_points = (
                    9 if gw_completed and stats["minutes"] == 0 else stats["points"]
                )
                try:
                    footballer_performance = anti.FootballerPerformanceAnti.objects.get(
                        gw=self.gw, footballer__id=footballer_id
                    )
                    # anti.FootballerPerformanceAnti.objects.filter(
                    #     gw=self.gw, footballer__id=footballer_id
                    # ).update(
                    #     minutes=stats["minutes"],
                    #     points=stats["points"],
                    #     anti_points=anti_points,
                    # )
                    footballer_performance.minutes = stats["minutes"]
                    footballer_performance.points = stats["points"]
                    footballer_performance.anti_points = anti_points
                    footballer_performance.save()
                except ObjectDoesNotExist:
                    break_flag = True
                    break
        if break_flag:
            self.start_stats_footballer()
            return None

        if gw_completed:
            # Update season player statistics
            self.update_gw_form_stats_footballer()

            Gameweek.objects.filter(id=self.gw).update(
                stats_completed=True, last_stats_updated=timezone.now()
            )

    def start_stats_footballer(self):
        """Get and store the static stats for the GW

        This includes, player ownerships (starting xi, squad)
        captaincy selections
        """
        self.gameweek_picks = GameweekPicks(gw=self.gw)
        all_managers_picks = self.gameweek_picks.get_gw_picks()

        footballer_dict = defaultdict(
            lambda: {"starting_xi": 0, "squad_xv": 0, "captains": 0, "cvc": 0}
        )

        for team_id, gw_picks in all_managers_picks.items():
            picks = Picks(gw_picks)

            # Update both captain and vice captain for this pick
            footballer_dict[picks.squad.captain]["captains"] += 1
            footballer_dict[picks.squad.captain]["cvc"] += 1
            footballer_dict[picks.squad.vice_captain]["cvc"] += 1

            for footballer, multiplier in picks.squad.team:
                # team is tuple of (player, multiplier)
                if multiplier:
                    footballer_dict[footballer]["starting_xi"] += 1
                footballer_dict[footballer]["squad_xv"] += 1

        # At this point the dict is constructed
        # We need to get all the players in the game
        # To get all the players, we can use gameweek_service method to get all players mintues
        # And for any player in the dict add this data
        # Get the points scored by all the players
        all_players_minutes = self.gameweek_service.get_players_minutes()

        for footballer_id in all_players_minutes.keys():
            try:
                footballer = Footballer.objects.get(id=footballer_id)
            except ObjectDoesNotExist:
                # this means that the data about footballers isn't up to date
                # new players are added, so refresh data
                add_update_footballers_meta()
                continue

            with transaction.atomic():
                stat = footballer_dict[footballer_id]
                try:
                    anti.FootballerPerformanceAnti.objects.create(
                        footballer=footballer,
                        gw=Gameweek.objects.get(id=self.gw),
                        starting_xi=stat["starting_xi"],
                        squad_xv=stat["squad_xv"],
                        captains=stat["captains"],
                        cvc=stat["cvc"],
                    )
                except Exception as e:
                    print(e)
                    # This entry is already created

    def get_anti_points_table(self):

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
                Gameweek.objects.filter(id=self.gw).update(is_current=True)
                Gameweek.objects.filter(id=self.gw - 1).update(is_current=False)
            # return anti.PointsTable.objects.filter(gw=self.gw)

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
            minutes=st.MAX_REFRESH_MINS
        ):
            self.update_gameweek()
        print(
            timezone.now(),
            self.gameweek.last_updated
            + datetime.timedelta(minutes=st.MAX_REFRESH_MINS),
        )
        return anti.PointsTable.objects.filter(gw=self.gw)

    def get_footballer_stats(self):
        # Check comments for get_data
        try:
            self.gameweek = Gameweek.objects.get(id=self.gw)
        except ObjectDoesNotExist:
            print(f"Raise Error - get_data - {self.gw}")

        if self.gameweek.completed and self.gameweek.stats_completed:
            return anti.FootballerPerformanceAnti.objects.filter(gw=self.gw)

        if self.gameweek.completed:
            # Stats not completed
            self.update_dynamic_stats_footballer(gw_completed=True)
            return anti.FootballerPerformanceAnti.objects.filter(gw=self.gw)

        if timezone.now() > self.gameweek.last_stats_updated + datetime.timedelta(
            minutes=st.MAX_REFRESH_MINS
        ):
            self.update_dynamic_stats_footballer()
        return anti.FootballerPerformanceAnti.objects.filter(gw=self.gw)
