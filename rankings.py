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

        [self.historical_ranks.update(week=self.get_season_ranks(last_week=week)) for week in range(1, league.current_week)]
        self.sorted_historical_ranks = [(ranks_to_sorted_array(self.get_season_ranks(last_week=week)), week) for week in range(1, league.current_week)]

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
                now = datetime.utcnow() + PST.utcoffset(datetime.utcnow())
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
                season_ranks[team_id].avg_rank += float(round(week_rank.rank / len(self.week_ranks.keys()), 2))

        sorted_season_ranks = ranks_to_sorted_array(season_ranks)
        for i in range(len(sorted_season_ranks)):
            week_rank = sorted_season_ranks[i]
            season_ranks[week_rank[0]].overall_rank = i + 1

        return season_ranks

    def set_week_ranks(self):
        self.week_ranks = {}
        now = datetime.utcnow() + PST.utcoffset(datetime.utcnow())
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

            if week in self.week_ranks:
                self.rank_teams(week)

    def rank_teams(self, week):
        self.week_ranks[week].sort(key=lambda team_rank: team_rank.team_points, reverse=True)
        teams_id_to_rank = {}
        rank = 1
        skip_from_draw_list = []

        for i in range(len(self.week_ranks[week])):
            week_rank = self.week_ranks[week][i]

            if week_rank.team.team_id in skip_from_draw_list:
                continue

            teams_id_to_rank[week_rank.team.team_id] = rank

            if week_rank.draw:
                teams_id_to_rank[week_rank.opponent.team_id] = rank
                skip_from_draw_list.append(week_rank.opponent.team_id)

            rank += 1

        for rank in self.week_ranks[week]:
            rank.rank = teams_id_to_rank[rank.team.team_id]
            rank.outscores = self.league.num_teams - rank.rank - (1 if rank.win else 0)
            rank.ranking_points = self.win_value * rank.win * 1 + self.draw_value * rank.draw * 1 + self.outscore_value * rank.outscores


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
        self.outscores = None
        self.rank = None
        self.ranking_points = None
        self.game_week = game_week
        self.week = game_week.week.number
        self.team = team
        self.opponent = opponent
        self.win = team_points > opponent_points
        self.draw = team_points == opponent_points
        self.result = None
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
