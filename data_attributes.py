import pytz


def join(*args):
    return '.'.join(args)


FANTASY_CONTENT = 'fantasy_content'
YAHOO_DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%d %H:%M:%S %Z%z'
PST = pytz.timezone('US/Pacific')


class GameAttrs:
    GAME_KEY = join(FANTASY_CONTENT, 'games.game.game_key.cdata')
    STAT_CATEGORIES = join(FANTASY_CONTENT, 'games.game.game_key.cdata')


class LeagueAttrs:
    LEAGUE = join(FANTASY_CONTENT, 'league')
    WEEK_SCOREBOARD = join(LEAGUE, 'scoreboard')
    NUM_TEAMS = join(LEAGUE, 'num_teams.cdata')
    NAME = join(LEAGUE, 'name.cdata')
    URL = join(LEAGUE, 'url.cdata')

    CURRENT_WEEK = join(LEAGUE, 'current_week.cdata')
    START_WEEK = join(LEAGUE, 'start_week.cdata')
    END_WEEK = join(LEAGUE, 'end_week.cdata')
    START_DATE = join(LEAGUE, 'start_date.cdata')
    END_DATE = join(LEAGUE, 'end_date.cdata')


class MatchupAttrs:
    WEEK_MATCHUPS = join(LeagueAttrs.WEEK_SCOREBOARD, 'matchups.matchup')
    WEEK_START_DATE = 'week_start.cdata'
    WEEK_END_DATE = 'week_end.cdata'
    STATUS = 'status.cdata'
    MATCHUP_TEAMS = 'teams.team'
    MATCHUP_TEAM_POINTS = 'team_points.total.cdata'


class TeamAttrs:
    TEAM = join(FANTASY_CONTENT, 'team')
    TEAMS = join(LeagueAttrs.LEAGUE, 'teams.team')
    TEAM_MATCHUPS = join(TEAM, 'matchups.matchup')
    TEAM_POINTS = join(TEAM, 'team_points.total.cdata')

    TEAM_ID = 'team_id.cdata'
    TEAM_KEY = 'team_key.cdata'
    TEAM_NAME = 'name.cdata'

    TEAM_PLAYERS = join(TEAM, 'roster.players.player')
