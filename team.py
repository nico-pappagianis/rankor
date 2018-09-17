class Team:
    def __init__(self, team_data):
        self.team_id = team_data.team_id.cdata
        self.key = team_data.team_key.cdata
        self.name = team_data.name.cdata

        self.wins = 0
        self.outscores = 0
        self.draws = 0
        self.ranking_points = 0
        self.matchups = {}
        self.week_results = {}

    def add_week_result(self, result):
        self.week_results[result.week_number] = result

    def add_week_result_from_matchup(self, matchup):
        self.week_results[matchup.week_number] = self.get_week_result(matchup)

    def get_week_result(self, matchup):
        return Team.WeekResult(matchup.team1_id,
                               matchup.team2_id,
                               matchup.week_number,
                               matchup.team1_points,
                               matchup.team1_points > matchup.team2_points,
                               matchup.team1_points == matchup.team2_points)

    def __str__(self):
        return 'Team {team_id}: {name}'.format(team_id=self.team_id, name=self.name)

    class WeekResult:
        def __init__(self, own_id, opponent_id, week_number, points, win, draw=False):
            self.own_id = own_id
            self.points = points
            self.week_number = week_number
            self.win = win
            self.draw = draw
            self.opponent_id = opponent_id
            self.outscores = None

        def __str__(self):
            return 'Week {week_number}: Team {own_id} {outcome}, {points} - vs Team {opponent_id}' \
                .format(week_number=self.week_number, outcome='Wins' if self.win else 'Loses', points=self.points,
                        own_id=self.own_id, opponent_id=self.opponent_id)
