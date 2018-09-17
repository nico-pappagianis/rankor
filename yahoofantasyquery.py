import requests
from http import HTTPStatus
from auth import Auth
import untangle
from urllib.parse import urljoin

YAHOO_API_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/'
LEAGUE_URL = urljoin(YAHOO_API_URL, 'league/{league_key}')
LEAGUE_STANDINGS_URL = urljoin(YAHOO_API_URL, 'league/{league_key}/standings')
LEAGUE_TEAMS_URL = urljoin(YAHOO_API_URL, 'league/{league_key}/teams')
LEAGUE_FILTER_URL = urljoin(YAHOO_API_URL, 'games;game_codes={game_codes};seasons={seasons}')
SCOREBOARD_URL_FMT = urljoin(YAHOO_API_URL, 'league/380.l.1067871/scoreboard;week={week_number}')
TEAM_STATS_URL_FMT = urljoin(YAHOO_API_URL, '/fantasy/v2/team/{team_key}/stats;type=week=')
TEAM_MATCHUPS_URL_FMT = urljoin(YAHOO_API_URL, '/fantasy/v2/team/{team_key}/matchups')


AUTHORIZATION = 'Authorization'
BEARER_AUTH_FMT = 'Bearer {token}'

auth = Auth()


def find_game_key(game_code, season):
    return _get(
        LEAGUE_FILTER_URL.format(game_codes=game_code, seasons=season)).fantasy_content.games.game.game_key.cdata


def get_league_data(league_key):
    return _get(LEAGUE_URL.format(league_key=league_key)).fantasy_content.league


def get_league_teams(league_key):
    return _get(LEAGUE_TEAMS_URL.format(league_key=league_key)).fantasy_content.league.teams.team


def get_league_standings(league_key):
    return _get(LEAGUE_STANDINGS_URL.format(league_key=league_key))


def get_matchups_for_week(week_number):
    return _get(SCOREBOARD_URL_FMT.format(week_number=week_number)).fantasy_content.league.scoreboard.matchups.matchup


def get_matchups_for_team(team_key):
    return _get(TEAM_MATCHUPS_URL_FMT.format(team_key=team_key)).fantasy_content.team.matchups.matchup


def get_team_stats(team_key):
    return _get(TEAM_STATS_URL_FMT.format(team_key=team_key)).fantasy_content.team


def _get(url, retry=True):
    res = requests.get(url, params={'format': 'xml'}, headers=headers())
    if retry and res.status_code == HTTPStatus.UNAUTHORIZED:
        auth.refresh_access_token()
        return _get(url, False)
    return untangle.parse(res.text)


def headers():
    return {AUTHORIZATION: BEARER_AUTH_FMT.format(token=auth.access_token)}

