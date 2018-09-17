from matchup import Matchup


class LeagueRankings:
    def __init__(self, league):
        self.league = league
        self.week_ranks = {}
        self.season_ranks = {}

    def rank(self):

        for week, matchups in self.league.matchups.items():
            self.week_ranks[week] = []

            for matchup in matchups:
                if matchup.status != Matchup.Status.POST_EVENT.value:
                    continue

                team1 = self.league.teams[matchup.team1_id]
                team2 = self.league.teams[matchup.team2_id]

                if matchup.team1_points > matchup.team2_points:
                    team1.wins += 1

                if matchup.team1_points < matchup.team2_points:
                    team2.wins += 1

                if matchup.team1_points == matchup.team2_points:
                    team1.draws += 1
                    team2.draws += 1

                self.week_ranks[week].append(Ranking(team1, team2, matchup.team1_points, matchup.draw))
                self.week_ranks[week].append(Ranking(team2, team1, matchup.team2_points, matchup.draw))

            self.rank_teams(week)

    def rank_teams(self, week_number):
        self.week_ranks[week_number].sort(key=lambda team_rank: team_rank.points, reverse=True)
        teams_id_to_rank = {}
        position = 1
        skip_from_draw_list = []
        for i in range(len(self.week_ranks[week_number])):
            team_rank = self.week_ranks[week_number][i]

            if team_rank.team.team_id in skip_from_draw_list:
                continue

            teams_id_to_rank[team_rank.team.team_id] = position

            if team_rank.draw:
                teams_id_to_rank[team_rank.opponent.team_id] = position
                skip_from_draw_list.append(team_rank.opponent.team_id)

            position += 1

        for rank in self.week_ranks[week_number]:
            rank.position = teams_id_to_rank[rank.team.team_id]


class Ranking:
    def __init__(self, team, opponent, points, draw, position=None):
        self.team = team
        self.opponent = opponent
        self.position = position
        self.points = points
        self.draw = draw
