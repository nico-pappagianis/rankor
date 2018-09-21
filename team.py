import os

from data_attributes import TeamAttrs
from fantasy_data import FantasyData, get_attribute

TEAM_DATA_FILE = 'teams.data'
TEAM_DATA_DIR = os.path.join('{data_dir}', 'teams')
TEAM_DATA_PATH = os.path.join(TEAM_DATA_DIR, TEAM_DATA_FILE)

TEAM_QUERY = 'league/{league_key}/teams'


class Team:
    def __init__(self, team_id, team_key, name):
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.team_id = team_id
        self.team_key = team_key
        self.name = name

    def __str__(self):
        return 'Team {team_id}: {name}'.format(team_id=self.team_id, name=self.name)


class TeamData(FantasyData):
    def __init__(self, league):
        self.teams = {}
        super(TeamData, self).__init__(api_query=TEAM_QUERY.format(league_key=league.league_key))

        teams_data = self.get_attribute(TeamAttrs.TEAMS)
        for team_data in teams_data:
            team_id = int(get_attribute(team_data, TeamAttrs.TEAM_ID))
            self.teams[team_id] = (Team(team_id=team_id,
                                        team_key=get_attribute(team_data, TeamAttrs.TEAM_KEY),
                                        name=get_attribute(team_data, TeamAttrs.TEAM_NAME)))
