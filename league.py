import logging
import os
from datetime import datetime

from data_attributes import LeagueAttrs, GameAttrs, PST
from fantasy_data import FantasyData, load, save
from matchup import MatchupsData
from rankings import LeagueRankings
from serializable import Serializable
from team import TeamData

GAMES_DATA_DIR = os.path.join('data', 'games')
GAME_CODE_DATA_DIR = os.path.join(GAMES_DATA_DIR, '{game_code}')
GAME_SEASON_DATA_DIR = os.path.join(GAME_CODE_DATA_DIR, '{season}')
GAME_KEY_DATA_FILE = 'key.data'

LEAGUE_DATA_FILE = 'league.data'
LEAGUE_DATA_DIR_FMT = os.path.join(GAME_SEASON_DATA_DIR, 'leagues', '{league_id}')
LEAGUE_FILE_FMT = os.path.join(LEAGUE_DATA_DIR_FMT, LEAGUE_DATA_FILE)

GAME_WEEK_DATA_FILE = 'game-week.data'
WEEK_DATA_DIR = os.path.join('{league_data_dir}', 'week-{week}')
GAME_WEEK_DATA_PATH = os.path.join(WEEK_DATA_DIR, GAME_WEEK_DATA_FILE)

LEAGUE_API_QUERY_FMT = 'league/{league_key}/standings'
GAME_KEY_QUERY = 'games;game_codes={game_code};seasons={season}'

logger = logging.getLogger(__name__)


class League(Serializable):
    def __init__(self, game_code, season, league_id):
        super(League, self).__init__()
        self.overall_results = {}
        self.game_weeks = {}
        self.teams = {}

        self.num_regular_season_games = None
        self.league_key = None
        self.num_teams = None
        self.name = None
        self.url = None
        self.current_week = None
        self.start_week = None
        self.end_week = None
        self.start_date = None
        self.end_date = None

        self.game_code = game_code
        self.season = season
        self.league_id = league_id

        self.data_dir = LEAGUE_DATA_DIR_FMT.format(game_code=game_code, league_id=league_id, season=season)
        self.data_filename = LEAGUE_DATA_FILE
        self.data_path = os.path.join(self.data_dir, self.data_filename)

        league = load(self.data_path)
        if league:
            logger.info('Loaded league data from path: {path}'.format(path=self.data_path))
            self.__dict__ = league.__dict__
        else:
            self.__init_from_data()

        self.__load_weeks()
        self.current_week_start_time = self.game_weeks[self.current_week].week.start_day.start_time
        self.current_week_end_time = self.game_weeks[self.current_week].week.end_day.end_time
        self.__update_current_week()

        self.__save()

    def refresh_current_week(self):
        if self.game_weeks[self.current_week].week_in_progress:
            self.game_weeks[self.current_week] = MatchupsData(self, self.current_week).game_week

    def __save(self):
        save(self, self.data_dir, self.data_filename)
        for week, game_week in self.game_weeks.items():
            data_dir = WEEK_DATA_DIR.format(league_data_dir=self.data_dir, week=week)
            save(game_week, data_dir, GAME_WEEK_DATA_FILE)
            logger.info('Saved week {week} data to path: {path} filename: {filename}'
                        .format(week=week, path=data_dir, filename=GAME_WEEK_DATA_FILE))

    def __load_weeks(self):
        for week in range(self.start_week, self.end_week + 1):
            if not self.__load_week(week):
                logger.info('Downloading data for GameWeek {week}'.format(week=week))
                game_week = MatchupsData(self, week).game_week
                if game_week:
                    self.game_weeks[week] = game_week

    def __load_week(self, week):
        game_week = load(GAME_WEEK_DATA_PATH.format(league_data_dir=self.data_dir, week=week))
        if game_week:
            self.game_weeks[week] = game_week
            logger.info('Loaded data for GameWeek {week}'.format(week=week))
            return True
        return False

    def __update_current_week(self):
        now = datetime.utcnow() + PST.utcoffset(datetime.utcnow())
        if self.current_week_end_time <= now:
            logger.info('Updating current week. End of week {week}'.format(week=self.current_week))
            league_data = LeagueData(self.game_code, self.season, self.league_id)
            self.current_week = int(league_data.get_attribute(LeagueAttrs.CURRENT_WEEK))
            logger.info('Current week is now {week}'.format(week=self.current_week))
        self.refresh_current_week()

    def __init_from_data(self):
        logger.info('Downloading league data...')
        league_data = LeagueData(self.game_code, self.season, self.league_id)
        logger.info('Done downloading league data.')

        self.game_code = league_data.game_code
        self.season = league_data.season
        self.league_id = league_data.league_id
        self.league_key = league_data.league_key

        self.current_week = int(league_data.get_attribute(LeagueAttrs.CURRENT_WEEK))
        self.num_teams = int(league_data.get_attribute(LeagueAttrs.NUM_TEAMS))
        self.name = league_data.get_attribute(LeagueAttrs.NAME)
        self.url = league_data.get_attribute(LeagueAttrs.URL)

        self.start_week = int(league_data.get_attribute(LeagueAttrs.START_WEEK))
        self.end_week = int(league_data.get_attribute(LeagueAttrs.END_WEEK))
        self.start_date = league_data.get_attribute(LeagueAttrs.START_DATE)
        self.end_date = league_data.get_attribute(LeagueAttrs.END_DATE)
        self.teams = TeamData(self).teams

        for week in reversed(range(self.start_week, self.end_week + 1)):
            if not self.num_regular_season_games:
                if MatchupsData(self, week).game_week:
                    self.num_regular_season_games = week + 1
                    break

    @property
    def latest_week(self):
        return self.current_week if self.game_weeks[self.current_week].week_in_progress else self.current_week - 1

    @staticmethod
    def get_in_progress_data(league_data_path):
        league = load(league_data_path)
        if not league:
            logger.warning('No league data in path: {path}'.format(path=league_data_path))
            return None
        else:
            logger.info('Loaded league data from path: {path}'.format(path=league_data_path))
        if not league.game_weeks[league.current_week].week_in_progress:
            logger.info('Current week is not in progress.')
            return None

        league.game_weeks[league.current_week] = MatchupsData(league, league.current_week).game_week
        league.__save()
        rankings = LeagueRankings(league, 10, 5, 1)
        return rankings


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
