import os

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

import forms
from league import League
from rankings import LeagueRankings, RankChange

flask_app = Flask(__name__)
flask_app.jinja_env.filters['zip'] = zip

flask_app.config.update(dict(
    SECRET_KEY=os.urandom(24),
    WTF_CSRF_SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True
))
flask_app.config['DEBUG'] = True

Bootstrap(flask_app)


@flask_app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@flask_app.route('/')
def index():
    league_form = forms.LeagueSetup()
    return render_template('home.html', league_form=league_form)


@flask_app.route('/league', methods=['POST'])
def league():
    league = League(game_code=request.form['game_code'], season=request.form['season'],
                    league_id=request.form['league_id'])
    rankings = LeagueRankings(league, 10, 5, 1)
    return render_template('rankings.html', league=league, rankings=rankings, RankChange=RankChange)


if __name__ == '__main__':
    flask_app.run()
