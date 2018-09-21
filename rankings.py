from matchup import Matchup


class LeagueRankings:
    def __init__(self, league):
        self.league = league
        self.week_ranks = {}
        self.season_ranks = {}

    def rank(self):

        for week, matchups in self.league.week_matchups.items():
            self.week_ranks[week] = []

            for matchup in matchups:
                if matchup.status != Matchup.Status.POST_EVENT:
                    continue

                team1 = matchup.team1
                team2 = matchup.team2

                if matchup.team1_points > matchup.team2_points:
                    team1.wins += 1
                    team2.losses += 1

                if matchup.team1_points < matchup.team2_points:
                    team2.wins += 1
                    team1.losses += 1

                if matchup.team1_points == matchup.team2_points:
                    team1.draws += 1
                    team2.draws += 1

                self.week_ranks[week].append(Ranking(team1, team2, matchup.team1_points, matchup.team2_points))
                self.week_ranks[week].append(Ranking(team2, team1, matchup.team2_points, matchup.team1_points))

            self.rank_teams(week)

    def rank_teams(self, week):
        self.week_ranks[week].sort(key=lambda team_rank: team_rank.team_points, reverse=True)
        teams_id_to_rank = {}
        position = 1
        skip_from_draw_list = []
        for i in range(len(self.week_ranks[week])):
            team_rank = self.week_ranks[week][i]

            if team_rank.team.team_id in skip_from_draw_list:
                continue

            teams_id_to_rank[team_rank.team.team_id] = position

            if team_rank.team_points == team_rank.opponent_points:
                teams_id_to_rank[team_rank.opponent.team_id] = position
                skip_from_draw_list.append(team_rank.opponent.team_id)

            position += 1

        for rank in self.week_ranks[week]:
            rank.position = teams_id_to_rank[rank.team.team_id]


class Ranking:
    def __init__(self, team, opponent, team_points, opponent_points, position=None):
        self.team = team
        self.opponent = opponent
        self.position = position
        self.team_points = team_points
        self.opponent_points = opponent_points

    def __str__(self):
        return '{team} {team_points} vs {opponent} {opponent_points}'.format(team=self.team,
                                                                             team_points=self.team_points,
                                                                             opponent=self.opponent,
                                                                             opponent_points=self.opponent_points)
