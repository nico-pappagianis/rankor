import json
import os
import jsonpickle
from flask import render_template, request, jsonify

import forms
from league import League
from rankings import LeagueRankings, RankChange


import flask
from flask_log import Logging
formatter = (
            '[%(asctime)s] %(levelname)s [%(name)s] '
            '%(filename)s:%(lineno)d - %(message)s')
app = flask.Flask(__name__)
app.config['FLASK_LOG_LEVEL'] = 'DEBUG'
flask_log = Logging(app)

Logging.set_formatter(formatter)

app.jinja_env.filters['zip'] = zip

app.config.update(dict(
    SECRET_KEY=os.urandom(24),
    WTF_CSRF_SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True
))
app.config['DEBUG'] = True



@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/')
def index():
    league_form = forms.LeagueSetup()
    return render_template('home.html', league_form=league_form)


@app.route('/rank', methods=['POST'])
@app.route('/rank/<game_code>/<season>/<league_id>', methods=['GET'])
def rank(game_code=None, season=None, league_id=None):
    if request.method == 'GET':
        league = League(game_code, season, league_id)
    else:
        league = League(game_code=request.form['game_code'], season=request.form['season'],
                        league_id=request.form['league_id'])
    rankings = LeagueRankings(league, 10, 5, 1)
    return render_template('league-rankings.html', league=league, rankings=rankings, RankChange=RankChange, jsonpickle=jsonpickle)


@app.route('/update_in_progress_games')
def update_in_progress_games():
    league_data_path = request.args.get('league_data_path')
    return jsonify(json.dumps(League.get_in_progress_data(league_data_path)))


if __name__ == '__main__':
    app.run()
