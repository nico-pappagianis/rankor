from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField
from wtforms.validators import DataRequired

class LeagueSetup(FlaskForm):
    game_code = SelectField(label='Game', choices=[('nfl', 'NFL')])
    season = SelectField(label='Season', choices=[(2018, 2018)])
    league_id = IntegerField(label='League ID')
