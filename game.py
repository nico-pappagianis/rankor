import os
from serializable import Serializable
from fantasy_data import FantasyData
from data_attributes import GameAttrs

GAMES_DATA_DIR = os.path.join('data', 'games')
GAME_CODE_DATA_DIR = os.path.join(GAMES_DATA_DIR, '{game_code}')
GAME_SEASON_DATA_DIR = os.path.join(GAME_CODE_DATA_DIR, '{season}')
GAME_KEY_DATA_FILE = 'key.data'

GAME_KEY_QUERY = 'games;game_codes={game_code};seasons={season}'


class Game(Serializable):
    def __init__(self, key, name, season, stat_categories, positions):
        super(Game, self).__init__()


class GameData(FantasyData):
    def __init__(self, game_code, season):
        self.game_key = None

        super(GameData, self).__init__(api_query=GAME_KEY_QUERY.format(game_code=game_code, season=season))
        self.game_key = self.get_attribute(GameAttrs.GAME_KEY)
