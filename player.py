from fantasy_data import FantasyData
from serializable import Serializable
PLAYERS_QUERY = 'players;player_keys={player_keys}'
KEY_DELIM = ','


class Player(Serializable):
    def __init__(self, key, id, name, position, nfl_team_name, nfl_team_abbr, bye_week, ):
        super(Player, self).__init__()
        self.name


class PlayerData(FantasyData):
    def __init__(self, *player_keys):
        super(PlayerData, self).__init__(api_query=PLAYERS_QUERY.format(player_keys=KEY_DELIM.join(player_keys)))
