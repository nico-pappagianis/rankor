import logging
import os
from datetime import datetime, timedelta
from enum import Enum, IntEnum

from data_attributes import MatchupAttrs, TeamAttrs, YAHOO_DATE_FMT, DATETIME_FMT, PST
from fantasy_data import FantasyData, get_attribute
from serializable import Serializable

SEASON_MATCHUPS_FILE = os.path.join('{league_data_dir}', 'season-matchups.data')
WEEK_MATCHUPS_DIR = os.path.join('{league_data_dir}', 'matchups')
WEEK_MATCHUPS_FILE = 'week-{week}.data'
WEEK_MATCHUPS_QUERY = 'league/{league_key}/scoreboard;week={week}'
TEAM_MATCHUP_QUERY = 'team/{team_key}/matchups'

logger = logging.getLogger(__name__)


class GameDay(Serializable):
    def __init__(self, start_time, end_time):
        super(GameDay, self).__init__()
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return '{start_time} - {end_time}'.format(start_time=self.start_time.strftime(DATETIME_FMT),
                                                  end_time=self.end_time.strftime(DATETIME_FMT))


class Week(Serializable):
    class Days(IntEnum):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

    def __init__(self, number, week_start_time, week_end_time):
        super(Week, self).__init__()
        self.number = number
        self.__week_start_time = PST.localize(week_start_time)
        self.__week_end_time = PST.localize(week_end_time)

        self.start_day = GameDay(self._get_thursday_start_time(), self._get_thursday_end_time())
        self.end_day = GameDay(self._get_monday_start_time(), self._get_monday_end_time())

    def __str__(self):
        return '{start_day} - {end_day}'.format(start_day=self.start_day, end_day=self.end_day)

    def __get_thursday(self):
        itr_datetime = self.__week_start_time
        while itr_datetime.weekday() != Week.Days.THURSDAY.value:
            itr_datetime += timedelta(1)
        return itr_datetime

    def __get_sunday(self):
        itr_datetime = self.__week_start_time
        while itr_datetime.weekday() != Week.Days.SUNDAY.value:
            itr_datetime += timedelta(1)
        return itr_datetime

    def __get_monday(self):
        itr_datetime = self.__week_start_time
        while itr_datetime.weekday() != Week.Days.MONDAY.value:
            itr_datetime += timedelta(1)
        return itr_datetime

    def _get_thursday_start_time(self):
        return self.__get_thursday().replace(hour=17, minute=20)

    def _get_thursday_end_time(self):
        return self.__get_thursday().replace(hour=23, minute=59, second=59)

    def _get_sunday_start_time(self):
        return self.__get_sunday().replace(hour=10, minute=00)

    def _get_sunday_end_time(self):
        return self.__get_sunday().replace(hour=23, minute=59, second=59)

    def _get_monday_start_time(self):
        return self.__get_monday().replace(hour=17, minute=15)

    def _get_monday_end_time(self):
        return self.__get_monday().replace(hour=23, minute=59, second=59)


class GameWeek(Serializable):
    class Status(Enum):
        POST_EVENT = 'postevent'
        PRE_EVENT = 'preevent'
        MID_EVENT = 'midevent'

    def __init__(self, week_number, start_datetime, end_datetime, matchups=None):
        super(GameWeek, self).__init__()
        self.week = Week(week_number, start_datetime, end_datetime)
        self.matchups = matchups or []

    def add_matchup(self, matchup):
        self.matchups.append(matchup)

    @property
    def week_in_progress(self):
        now = PST.localize(datetime.now())
        if self.week.start_day.start_time <= now <= self.week.end_day.end_time:
            logger.info(
                'Week is in progress: week start day: {week_start_day},  current time: {now}, week end day: {week_end_day}'
                    .format(now=now.strftime(DATETIME_FMT),
                            week_start_day=self.week.start_day, week_end_day=self.week.end_day))
            return True

    def __str__(self):
        return 'Week: {week}, Matchups: {matchups}'.format(week=self.week, matchups=', '.join(self.matchups))


class Matchup(Serializable):

    def __init__(self, week, team1, team1_points, team2, team2_points):
        super(Matchup, self).__init__()
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
                start_date = datetime.strptime(get_attribute(matchup_data, MatchupAttrs.WEEK_START_DATE),
                                               YAHOO_DATE_FMT)
                end_date = datetime.strptime(get_attribute(matchup_data, MatchupAttrs.WEEK_END_DATE), YAHOO_DATE_FMT)
                self.game_week = GameWeek(week, start_date, end_date)

            teams = get_attribute(matchup_data, MatchupAttrs.MATCHUP_TEAMS)
            team1 = league.teams[int(get_attribute(teams[0], TeamAttrs.TEAM_ID))]
            team1_points = float(get_attribute(teams[0], MatchupAttrs.MATCHUP_TEAM_POINTS))
            team2 = league.teams[int(get_attribute(teams[1], TeamAttrs.TEAM_ID))]
            team2_points = float(get_attribute(teams[1], MatchupAttrs.MATCHUP_TEAM_POINTS))
            self.game_week.add_matchup(Matchup(week, team1, team1_points, team2, team2_points))
