import os
from datetime import datetime, timedelta
from enum import Enum, IntEnum

import pytz

from data_attributes import MatchupAttrs, TeamAttrs
from fantasy_data import FantasyData, get_attribute

SEASON_MATCHUPS_FILE = os.path.join('{league_data_dir}', 'season-matchups.data')
WEEK_MATCHUPS_DIR = os.path.join('{league_data_dir}', 'matchups')
WEEK_MATCHUPS_FILE = 'week-{week}.data'
WEEK_MATCHUPS_QUERY = 'league/{league_key}/scoreboard;week={week}'
TEAM_MATCHUP_QUERY = 'team/{team_key}/matchups'

PST = pytz.timezone('US/Pacific')


class GameWeek:
    class Days(IntEnum):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

    class Status(Enum):
        POST_EVENT = 'postevent'
        PRE_EVENT = 'preevent'
        MID_EVENT = 'midevent'

    def __init__(self, week, start_datetime, end_datetime, matchups=None):
        self.week = week
        self.start_date = GameWeek._get_start_datetime(start_datetime)
        self.end_date = GameWeek._get_end_datetime(end_datetime)
        self.matchups = matchups or []

    def add_matchup(self, matchup):
        self.matchups.append(matchup)

    @property
    def status(self):
        now = PST.localize(datetime.now())
        if now < self.start_date:
            return GameWeek.Status.PRE_EVENT
        elif self.start_date <= now <= self.end_date:
            return GameWeek.Status.MID_EVENT
        else:
            return GameWeek.Status.POST_EVENT

    @staticmethod
    def _get_start_datetime(start_datetime):
        itr_datetime = PST.localize(start_datetime)
        while itr_datetime.weekday() != GameWeek.Days.THURSDAY.value:
            itr_datetime += timedelta(1)
        return itr_datetime.replace(hour=17, minute=20)

    @staticmethod
    def _get_end_datetime(end_datetime):
        itr_datetime = PST.localize(end_datetime)
        while itr_datetime.weekday() != GameWeek.Days.TUESDAY.value:
            itr_datetime += timedelta(1)
        return itr_datetime.replace(hour=00, minute=00)


class Matchup:

    def __init__(self, week, team1, team1_points, team2, team2_points):
        self.week = week
        self.team1 = team1
        self.team1_points = team1_points
        self.team2 = team2
        self.team2_points = team2_points

    def __str__(self):
        return 'Week {week} - {team1} {team1_points} vs {team2_points} {team2}'.format(
            week=self.week,
            team1=self.team1, team1_points=self.team1_points,
            team2_points=self.team2_points, team2=self.team2)


class MatchupsData(FantasyData):
    def __init__(self, league, week):
        self.week = week
        self.game_week = None
        super(MatchupsData, self).__init__(
            api_query=WEEK_MATCHUPS_QUERY.format(league_key=league.league_key, week=week))

        matchups_data = self.get_attribute(MatchupAttrs.WEEK_MATCHUPS)
        for matchup_data in matchups_data:

            if not self.game_week:
                start_date = datetime.strptime(get_attribute(matchup_data, MatchupAttrs.WEEK_START_DATE), '%Y-%m-%d')
                end_date = datetime.strptime(get_attribute(matchup_data, MatchupAttrs.WEEK_END_DATE), '%Y-%m-%d')
                self.game_week = GameWeek(week, start_date, end_date)

            teams = get_attribute(matchup_data, MatchupAttrs.MATCHUP_TEAMS)
            team1 = league.teams[int(get_attribute(teams[0], TeamAttrs.TEAM_ID))]
            team1_points = float(get_attribute(teams[0], MatchupAttrs.MATCHUP_TEAM_POINTS))
            team2 = league.teams[int(get_attribute(teams[1], TeamAttrs.TEAM_ID))]
            team2_points = float(get_attribute(teams[1], MatchupAttrs.MATCHUP_TEAM_POINTS))
            self.game_week.add_matchup(Matchup(week, team1, team1_points, team2, team2_points))
