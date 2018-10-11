from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField


class LeagueSetup(FlaskForm):
    game_code = SelectField(label='Game', choices=[('nfl', 'NFL')])
    season = SelectField(label='Season', choices=[(2018, 2018)])
    league_id = IntegerField(label='League ID')


class StandingsComparison(FlaskForm):
    start_week = SelectField(label='Start Week', choices=[])
    end_week = SelectField(label='End Week', choices=[])
