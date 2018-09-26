import os
import pytz
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum

from data_attributes import MatchupAttrs, TeamAttrs
from fantasy_data import FantasyData, get_attribute

SEASON_MATCHUPS_FILE = os.path.join('{league_data_dir}', 'season-matchups.data')
WEEK_MATCHUPS_DIR = os.path.join('{league_data_dir}', 'matchups')
WEEK_MATCHUPS_FILE = 'week-{week}.data'
WEEK_MATCHUPS_QUERY = 'league/{league_key}/scoreboard;week={week}'
TEAM_MATCHUP_QUERY = 'team/{team_key}/matchups'

class GameWeekMatchups:
    def __init__(self, game_week, matchups=None):
        self.game_week = game_week
        self.matchups = matchups or []

    def add_matchup(self, matchup):
        self.matchups.append(matchup)


class GameWeek:
    class Days(IntEnum):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

    def __init__(self, week, start_datetime, end_datetime):
        self.week = week
        self.start_date = GameWeek._get_start_datetime(start_datetime)
        self.end_date = GameWeek._get_end_datetime(end_datetime)

    @staticmethod
    def _get_start_datetime(start_datetime):
        itr_datetime = pytz.timezone('US/Pacific').localize(start_datetime)
        while itr_datetime.weekday() != GameWeek.Days.THURSDAY.value:
            itr_datetime += timedelta(1)
        return itr_datetime.replace(hour=17, minute=20)

    @staticmethod
    def _get_end_datetime(end_datetime):
        itr_datetime = pytz.timezone('US/Pacific').localize(end_datetime)
        while itr_datetime.weekday() != GameWeek.Days.TUESDAY.value:
            itr_datetime += timedelta(1)
        return itr_datetime.replace(hour=00, minute=00)


class Matchup:
    class Status(Enum):
        POST_EVENT = 'postevent'
        PRE_EVENT = 'preevent'
        MID_EVENT = 'midevent'

    def __init__(self, league, matchup_data):
        self.week = matchup_data.week.cdata
        self.start_date = datetime.strptime(matchup_data.week_start.cdata, '%Y-%m-%d')
        self.end_date = datetime.strptime(matchup_data.week_end.cdata, '%Y-%m-%d')

        self.status = Matchup.Status(matchup_data.status)

        teams = get_attribute(matchup_data, MatchupAttrs.MATCHUP_TEAMS)
        self.team1 = league.teams[int(get_attribute(teams[0], TeamAttrs.TEAM_ID))]
        self.team1_points = float(get_attribute(teams[0], MatchupAttrs.MATCHUP_TEAM_POINTS))

        self.team2 = league.teams[int(get_attribute(teams[1], TeamAttrs.TEAM_ID))]
        self.team2_points = float(get_attribute(teams[1], MatchupAttrs.MATCHUP_TEAM_POINTS))

    def __str__(self):
        return 'Week {week} - {team1} {team1_points} vs {team2_points} {team2}'.format(
            week=self.week,
            team1=self.team1, team1_points=self.team1_points,
            team2_points=self.team2_points, team2=self.team2)


class WeekMatchups(FantasyData):
    def __init__(self, league, week):
        self.week = week
        self.matchups = []
        super(WeekMatchups, self).__init__(
            api_query=WEEK_MATCHUPS_QUERY.format(league_key=league.league_key, week=week))

        matchups_data = self.get_attribute(MatchupAttrs.WEEK_MATCHUPS)
        for matchup_data in matchups_data:
            self.matchups.append(Matchup(league, matchup_data))
