import os

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

import forms
from league import League
from rankings import LeagueRankings, RankChange

app = Flask(__name__)
app.jinja_env.filters['zip'] = zip

app.config.update(dict(
    SECRET_KEY=os.urandom(24),
    WTF_CSRF_SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True
))
app.config['DEBUG'] = True

Bootstrap(app)


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
    return render_template('league-rankings.html', league=league, rankings=rankings, RankChange=RankChange)


if __name__ == '__main__':
    app.run()
