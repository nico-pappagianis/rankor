from yahoo_fantasy import FantasyData
import yahoofantasyquery as query
import _pickle
import os
import logging
import leaguerankings
import goldfinch
from team import Team
from matchup import Matchup
from collections import namedtuple
import functools

LEAGUE_DATA_DIR_FMT = os.path.join('data', 'leagues', '{league_id}')
LEAGUE_FILE_FMT = os.path.join(LEAGUE_DATA_DIR_FMT, 'league.data')
LEAGUE_DATA_FILE = 'league.data'

LEAGUE_KEY_DATA_FILE = 'league_key.data'

WEEK_DATA_DIR = os.path.join(LEAGUE_DATA_DIR_FMT, 'week-{week_number}')
WEEK_MATCHUPS_DATA_DIR = os.path.join(WEEK_DATA_DIR, 'matchups')
WEEK_MATCHUPS_FILE_FMT = os.path.join(WEEK_MATCHUPS_DATA_DIR, 'matchups.data')


LEAGUE_API_QUERY_FMT = 'league/{league_key}'
LEAGUE_FILTER_QUERY_FMT = 'games;game_codes={game_codes};seasons={seasons}'

logger = logging.getLogger(__name__)


class LeagueData(FantasyData):

    def __init__(self, game_code, season, league_id):
        league_key_data = LeagueKey(game_code, season, league_id).get()
        a = rgetattr(league_key_data, 'fantasy_content.games.game.game_key.cdata')
        print(a)
        # super(LeagueData, self).__init__(api_query=LEAGUE_API_QUERY_FMT.format(league_key=self.league_key),
        #                                  data_dir=LEAGUE_DATA_DIR_FMT.format(league_id=league_id),
        #                                  data_file=LEAGUE_DATA_FILE)


class LeagueKey(FantasyData):
    def __init__(self, game_code, season, league_id):
        super(LeagueKey, self).__init__(
            api_query=LEAGUE_FILTER_QUERY_FMT.format(game_codes=game_code, seasons=season),
            data_dir=LEAGUE_DATA_DIR_FMT.format(league_id=league_id),
            data_file=LEAGUE_KEY_DATA_FILE)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

class League:

    def __init__(self, game_code, season, id):
        self.league_id = id
        self.season = season
        self.key = get_league_key(game_code, season, id)

        self.num_teams = None
        self.name = None
        self.url = None

        self.num_reg_season_games = None
        self.current_week = None
        self.start_week = None
        self.start_date = None
        self.end_week = None
        self.end_date = None

        self.overall_results = {}
        self.matchups = {}
        self.teams = {}

        self.set_league_data()
        self.save()

    def save(self):
        league_data_dir = LEAGUE_DATA_DIR_FMT.format(id=self.league_id)
        os.makedirs(league_data_dir, exist_ok=True)
        with open(LEAGUE_FILE_FMT.format(id=self.league_id), 'wb') as data_file:
            _pickle.dump(self, data_file)

    def load(self):
        data_file = LEAGUE_FILE_FMT.format(id=self.league_id)
        if os.path.exists(data_file):
            self.__dict__ = _pickle.load(open(data_file, 'rb')).__dict__
            self.refresh_league_data()
            return True
        return False

    def set_league_data(self):
        if not self.load():
            self.download_league_data()
            self.download_team_data()
            self.num_reg_season_games = len(query.get_matchups_for_team(next(iter(self.teams.values())).key))
            self.download_matchup_data()

    def download_league_data(self):
        league_data = query.get_league_data(self.key)

        self.num_teams = int(league_data.num_teams.cdata)
        self.name = league_data.name.cdata
        self.url = league_data.url.cdata

        self.current_week = int(league_data.current_week.cdata)
        self.start_week = int(league_data.start_week.cdata)
        self.end_week = int(league_data.end_week.cdata)
        self.start_date = league_data.start_date.cdata
        self.end_date = league_data.end_date.cdata

    def download_team_data(self):
        teams_data = query.get_league_teams(self.key)
        for i in range(len(teams_data)):
            team_data = teams_data[i]
            team = Team(team_data)
            self.teams[team_data.team_id.cdata] = team

    def download_matchup_data(self):

        for week_number in range(self.start_week, self.num_reg_season_games + 1):

            if week_number not in self.overall_results:
                self.overall_results[week_number] = []

            if week_number not in self.matchups:
                self.matchups[week_number] = []

            try:
                if self.matchups[week_number].status == Matchup.Status.POST_EVENT:
                    continue
            except AttributeError:
                pass

            week_matchups = query.get_matchups_for_week(week_number)
            for i in range(len(week_matchups)):
                matchup = Matchup(week_matchups[i])
                result = self.teams[matchup.team1_id].get_week_result(matchup)
                self.matchups[week_number].append(matchup)
                self.overall_results[week_number].append(result)
                self.teams[matchup.team1_id].add_week_result(result)

    def refresh_league_data(self):
        league_data = query.get_league_data(self.key)
        self.current_week = int(league_data.current_week.cdata)

    def __str__(self):
        return self.name

def get_league_key(game_code, season, id):
    game_key = query.find_game_key(game_code, season)
    return '.'.join([game_key, 'l', id])


