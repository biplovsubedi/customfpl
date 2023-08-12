LEAGUE_CODE_ANTI = "339171"


# Api endpoints for fpl
# Returns the gw points and other details of max 50 users as a page
URL_STANDINGS_BASE_ANTI = f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_CODE_ANTI}/standings/?page_standings="

URL_NEW_ENTRIES_ANTI = f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_CODE_ANTI}/standings/?page_new_entries="

# Returns the live points of all the players in that gw
URL_GW_LIVE = "https://fantasy.premierleague.com/api/event/{gw}/live/"

# Returns the gw picks for a manager in a gw
URL_GW_PICKS = "https://fantasy.premierleague.com/api/entry/{entry}/event/{gw}/picks/"

# Returns almost everything about FPL (Here it is used to check if a GW has been completed or not)
URL_BOOTSTRAP_STATIC = "https://fantasy.premierleague.com/api/bootstrap-static/"


"""
Endpoints:
https://fantasy.premierleague.com/api/entry/4621202/event/4/picks/  -> See picks for a player in a week
History of a player: https://fantasy.premierleague.com/api/entry/4621202/history/
https://fantasy.premierleague.com/api/leagues-classic/253269/standings/?page_standings=
"""
