from numbers import Number
from datetime import datetime
from enum import Enum

from data_attributes import PST
from serializable import Serializable


class RankChange(Serializable):
    class Direction(Enum):
        UP = 'up'
        DOWN = 'down'
        NONE = 'none'

    def __init__(self, current, prior):
        super(RankChange, self).__init__()
        self.current = current
        self.prior = prior
        if current > prior:
            self.direction = RankChange.Direction.UP
        elif current < prior:
            self.direction = RankChange.Direction.DOWN
        else:
            self.direction = RankChange.Direction.NONE


class LeagueRankings(Serializable):
    def __init__(self, league, win_value, draw_value, outscore_value):
        super(LeagueRankings, self).__init__()
        self.in_progress = league.game_weeks[league.current_week].week_in_progress
        self.win_value = win_value
        self.draw_value = draw_value
        self.outscore_value = outscore_value
        self.league = league
        self.week_ranks = {}
        self.historical_ranks = {}

        self.set_week_ranks()

        [self.historical_ranks.update(week=self.get_season_ranks(last_week=week)) for week in
         range(1, league.current_week)]
        self.sorted_historical_ranks = [(ranks_to_sorted_array(self.get_season_ranks(last_week=week)), week) for week in
                                        range(1, league.current_week)]

        self.season_ranks = self.get_season_ranks()
        self.season_ranks_prior = self.get_season_ranks(last_week=league.current_week - 1)
        self.season_ranks_in_progress = self.get_season_ranks(True)

        self.sorted_season_ranks = ranks_to_sorted_array(self.season_ranks)
        self.sorted_season_ranks_prior = ranks_to_sorted_array(self.season_ranks_prior)
        self.sorted_season_ranks_in_progress = ranks_to_sorted_array(self.season_ranks_in_progress)

        self.rank_changes = {}
        for current_rank, prior_rank in zip(self.season_ranks.values(), self.season_ranks_prior.values()):
            if not prior_rank.overall_rank:
                break
            self.rank_changes[current_rank.team.team_id] = RankChange(current_rank.overall_rank,
                                                                      prior_rank.overall_rank)

        self.in_progress_rank_changes = {}
        for current_rank, in_progress_rank in zip(self.season_ranks.values(), self.season_ranks_in_progress.values()):
            self.in_progress_rank_changes[current_rank.team.team_id] = RankChange(current_rank.overall_rank,
                                                                                  in_progress_rank.overall_rank)

    def get_season_ranks(self, include_in_progress=False, last_week=None):
        season_ranks = {}
        for team_id in self.league.teams.keys():
            season_ranks[team_id] = SeasonRank(self.league.teams[team_id])

        for week, week_ranks in self.week_ranks.items():
            if last_week and last_week < week:
                break

            for week_rank in week_ranks:
                now = PST.localize(datetime.utcnow() + PST.utcoffset(datetime.utcnow()))
                if now < week_rank.game_week.week.start_day.start_time:
                    continue

                if week_rank.game_week.week_in_progress:
                    if not include_in_progress:
                        continue

                team_id = week_rank.team.team_id
                season_ranks[team_id].wins += week_rank.win * 1
                season_ranks[team_id].draws += week_rank.draw * 1
                season_ranks[team_id].losses += not week_rank.win * 1
                season_ranks[team_id].outscores += week_rank.outscores
                season_ranks[team_id].avg_outscores += float(
                    round(week_rank.outscores / len(self.week_ranks.keys()), 2))
                season_ranks[team_id].ranking_points += week_rank.ranking_points

                if isinstance(week_rank.rank, Number):
                    season_ranks[team_id].avg_rank += float(round(week_rank.rank / len(self.week_ranks.keys()), 2))

        sorted_season_ranks = ranks_to_sorted_array(season_ranks)
        for i in range(len(sorted_season_ranks)):
            week_rank = sorted_season_ranks[i]
            season_ranks[week_rank[0]].overall_rank = i + 1

        return season_ranks

    def set_week_ranks(self):
        self.week_ranks = {}
        now = PST.localize(datetime.utcnow() + PST.utcoffset(datetime.utcnow()))
        for week, game_week in self.league.game_weeks.items():

            if now < game_week.week.start_day.start_time:
                continue

            for matchup in game_week.matchups:

                if week not in self.week_ranks:
                    self.week_ranks[week] = []

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

                self.week_ranks[week].append(
                    WeekRank(game_week, team1, team2, matchup.team1_points, matchup.team2_points))
                self.week_ranks[week].append(
                    WeekRank(game_week, team2, team1, matchup.team2_points, matchup.team1_points))

            self.week_ranks[week].sort(key=lambda team_rank: team_rank.team_points, reverse=True)

            if week in self.week_ranks:
                self.rank_teams(week)

    def rank_teams(self, week):
        self.rank_week(week)

    def rank_week(self, week):
        self.calculate_ranking_points(week)
        ranks = self.week_ranks[week]
        ranks.sort(key=lambda x: (x.ranking_points, x.team_points, x.win), reverse=True)
        for i, rank in enumerate(ranks, 1):
            if rank.team_points == 0:
                rank.rank = '-'
            else:
                rank.rank = i

    def calculate_ranking_points(self, week):
        self.calculate_outscores(week)
        ranks = self.week_ranks[week]
        for rank in ranks:
            if rank.team_points == 0:
                rank.ranking_points = 0
            else:
                rank.ranking_points = self.win_value * rank.win * 1 + self.draw_value * rank.draw * 1 + self.outscore_value * rank.outscores

    def calculate_outscores(self, week):
        ranks = self.week_ranks[week]

        for i, rank_being_sorted in enumerate(ranks):
            for other_rank in ranks[i + 1:]:

                if other_rank.team.team_id == rank_being_sorted.opponent.team_id:
                    continue

                if rank_being_sorted.team_points > other_rank.team_points:
                    rank_being_sorted.outscores += 1


def ranks_to_sorted_array(ranks):
    return sorted(ranks.items(), key=lambda kv: kv[1].ranking_points, reverse=True)


class SeasonRank(Serializable):
    def __init__(self, team):
        super(SeasonRank, self).__init__()
        self.team = team
        self.overall_rank = None
        self.avg_rank = 0
        self.outscores = 0
        self.avg_outscores = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.ranking_points = 0


class WeekRank(Serializable):
    def __init__(self, game_week, team, opponent, team_points, opponent_points):
        super(WeekRank, self).__init__()
        self.outscores = 0
        self.rank = None
        self.ranking_points = None
        self.game_week = game_week
        self.week = game_week.week.number
        self.team = team
        self.opponent = opponent
        self.win = team_points > opponent_points
        self.draw = team_points == opponent_points
        self.result = None
        if game_week.week_in_progress:
            self.result = '?'
        else:
            if self.win:
                self.result = 'W'
            elif self.draw:
                self.result = 'D'
            else:
                self.result = 'L'

        self.team_points = team_points
        self.opponent_points = opponent_points

    def __str__(self):
        return '{team} {team_points} vs {opponent} {opponent_points}'.format(team=self.team,
                                                                             team_points=self.team_points,
                                                                             opponent=self.opponent,
                                                                             opponent_points=self.opponent_points)
