from enum import Enum


class Matchup:
    class Status(Enum):
        POST_EVENT = 'postevent'
        PRE_EVENT = 'preevent'
        MID_EVENT = 'midevent'

    def __init__(self, matchup_data):
        self.week_number = matchup_data.week.cdata
        self.week_start = matchup_data.week_start.cdata
        self.week_end = matchup_data.week_end.cdata
        self.status = matchup_data.status.cdata

        team1_data = matchup_data.teams.team[0]
        self.team1_id = team1_data.team_id.cdata
        self.team1_name = team1_data.name.cdata
        self.team1_points = float(team1_data.team_points.total.cdata)

        team2_data = matchup_data.teams.team[1]
        self.team2_id = team2_data.team_id.cdata
        self.team2_name = team2_data.name.cdata
        self.team2_points = float(team2_data.team_points.total.cdata)

        self.draw = self.status == Matchup.Status.POST_EVENT and self.team1_points == self.team2_points

    def __str__(self):
        return 'Week {week_number}: ' \
               'Team {team1_id} - {team1_name} ({team1_points}) vs ' \
               'Team {team2_id} - {team2_name} ({team2_points})' \
            .format(week_number=self.week_number,
                    team1_id=self.team1_id, team1_name=self.team1_name, team1_points=self.team1_points,
                    team2_id=self.team2_id, team2_name=self.team2_name, team2_points=self.team2_points)
