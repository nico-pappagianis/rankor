import os

from data_attributes import TeamAttrs
from fantasy_data import FantasyData, get_attribute
from serializable import Serializable

TEAM_DATA_FILE = 'teams.data'
TEAM_DATA_DIR = os.path.join('{data_dir}', 'teams')
TEAM_DATA_PATH = os.path.join(TEAM_DATA_DIR, TEAM_DATA_FILE)

TEAM_QUERY = 'league/{league_key}/teams'
TEAM_WEEK_STATS_QUERY = 'team/{team_key}/stats;type=week;week={week}'
TEAM_WEEK_ROSTER_QUERY = 'team/{team_key}/roster;week={week}'


class Team(Serializable):
    def __init__(self, team_id, team_key, name):
        super(Team, self).__init__()
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.team_id = team_id
        self.team_key = team_key
        self.name = name
        self.roster = {}

    def __str__(self):
        return 'Team {team_id}: {name}'.format(team_id=self.team_id, name=self.name)

    @staticmethod
    def from_data(team_data):
        return Team(team_id=int(get_attribute(team_data, TeamAttrs.TEAM_ID)),
                    team_key=get_attribute(team_data, TeamAttrs.TEAM_KEY),
                    name=get_attribute(team_data, TeamAttrs.TEAM_NAME))


class TeamWeekStatsData(FantasyData):
    def __init__(self, team, week):
        super(TeamWeekStatsData, self).__init__(api_query=TEAM_WEEK_STATS_QUERY.format(team_key=team.team_key,
                                                                                       week=week))
        self.points = self.get_attribute(TeamAttrs.TEAM_POINTS)


class TeamWeekRosterData(FantasyData):
    def __init__(self, team, week):
        super(TeamWeekRosterData, self).__init__(api_query=TEAM_WEEK_ROSTER_QUERY.format(team_key=team.team_key,
                                                                                         week=week))
        players = self.get_attribute(TeamAttrs.TEAM_PLAYERS)
        for player in players:



class TeamData(FantasyData):
    def __init__(self, league):
        self.teams = {}
        super(TeamData, self).__init__(api_query=TEAM_QUERY.format(league_key=league.league_key))

        teams_data = self.get_attribute(TeamAttrs.TEAMS)
        for team_data in teams_data:
            team_id = int(get_attribute(team_data, TeamAttrs.TEAM_ID))
            self.teams[team_id] = Team(team_id=team_id,
                                       team_key=get_attribute(team_data, TeamAttrs.TEAM_KEY),
                                       name=get_attribute(team_data, TeamAttrs.TEAM_NAME))
