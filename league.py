import logging
import os

from data_attributes import LeagueAttrs, GameAttrs
from fantasy_data import FantasyData, load, save
from matchup import MatchupsData
from team import TeamData

GAMES_DATA_DIR = os.path.join('data', 'games')
GAME_CODE_DATA_DIR = os.path.join(GAMES_DATA_DIR, '{game_code}')
GAME_SEASON_DATA_DIR = os.path.join(GAME_CODE_DATA_DIR, '{season}')
GAME_KEY_DATA_FILE = 'key.data'

LEAGUE_DATA_FILE = 'league.data'
LEAGUE_DATA_DIR_FMT = os.path.join(GAME_SEASON_DATA_DIR, 'leagues', '{league_id}')
LEAGUE_FILE_FMT = os.path.join(LEAGUE_DATA_DIR_FMT, LEAGUE_DATA_FILE)

WEEK_DATA_DIR = os.path.join(LEAGUE_DATA_DIR_FMT, 'week-{week_number}')
WEEK_MATCHUPS_DATA_DIR = os.path.join(WEEK_DATA_DIR, 'matchups')
WEEK_MATCHUPS_FILE_FMT = os.path.join(WEEK_MATCHUPS_DATA_DIR, 'matchups.data')

LEAGUE_API_QUERY_FMT = 'league/{league_key}/standings'
GAME_KEY_QUERY = 'games;game_codes={game_code};seasons={season}'

logger = logging.getLogger(__name__)


class League:
    def __init__(self, game_code, season, league_id):
        self.data_dir = LEAGUE_DATA_DIR_FMT.format(game_code=game_code, league_id=league_id, season=season)
        self.data_filename = LEAGUE_DATA_FILE
        self.data_path = os.path.join(self.data_dir, self.data_filename)

        league = load(self.data_path)
        if league:
            self.__dict__ = league.__dict__
            return
        else:
            league_data = LeagueData(game_code, season, league_id)

        self.num_regular_season_games = None
        self.overall_results = {}
        self.game_weeks = {}
        self.teams = {}

        self.game_code = league_data.game_code
        self.season = league_data.season
        self.league_id = league_data.league_id
        self.league_key = league_data.league_key

        self.num_teams = int(league_data.get_attribute(LeagueAttrs.NUM_TEAMS))
        self.name = league_data.get_attribute(LeagueAttrs.NAME)
        self.url = league_data.get_attribute(LeagueAttrs.URL)

        self.current_week = int(league_data.get_attribute(LeagueAttrs.CURRENT_WEEK))
        self.start_week = int(league_data.get_attribute(LeagueAttrs.START_WEEK))
        self.end_week = int(league_data.get_attribute(LeagueAttrs.END_WEEK))
        self.start_date = league_data.get_attribute(LeagueAttrs.START_DATE)
        self.end_date = league_data.get_attribute(LeagueAttrs.END_DATE)

        self.teams = TeamData(self).teams

        for week in range(self.start_week, self.end_week + 1):
            game_week = MatchupsData(self, week).game_week
            if not game_week:
                if not self.num_regular_season_games:
                    self.num_regular_season_games = week - 1
            else:
                self.game_weeks[week] = game_week

        save(self, self.data_dir, self.data_filename)


class LeagueData(FantasyData):

    def __init__(self, game_code, season, league_id):
        self.game_code = game_code
        self.season = season
        self.league_id = league_id

        self.game_key = GameKeyData(game_code, season).game_key
        self.league_key = '.'.join([self.game_key, 'l', league_id])

        super(LeagueData, self).__init__(api_query=LEAGUE_API_QUERY_FMT.format(league_key=self.league_key))


class GameKeyData(FantasyData):
    def __init__(self, game_code, season):
        self.game_key = None

        super(GameKeyData, self).__init__(api_query=GAME_KEY_QUERY.format(game_code=game_code, season=season))
        self.game_key = self.get_attribute(GameAttrs.GAME_KEY)
