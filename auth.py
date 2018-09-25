from flask import Blueprint, request, sessions
import requests

# bp = Blueprint('auth', __name__, url_prefix='/auth')

KEY = 'dj0yJmk9YjBUTFJqTWRRTDNrJmQ9WVdrOU5qWkVja3RrTXpBbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1jYg--'
SECRET = 'b4293f4f33f0c4fbd94fe35e1a538f30aeffcb62'
REFRESH_TOKEN = 'AOrIhFvw9XDqC4c89LQTjDa8omlRKUw3CT9asqf_RD2j9BywrjVJeMPyNrVp3nfeLFM-'
TOKEN_URL = 'https://api.login.yahoo.com/oauth2/get_token'
CODE = '9hvuzj8'
BASIC_AUTH = 'Basic ' + KEY + ':' + SECRET


class Auth:

    def __init__(self):
        self.access_token = None

    def refresh_access_token(self):
        data = {
            'client_id': KEY,
            'json': True,
            'client_secret': SECRET,
            'refresh_token': REFRESH_TOKEN,
            'grant_type': 'refresh_token',
            'redirect_uri': 'oob',
            'headers': {
                'Authorization': BASIC_AUTH,
                'Content-Type': 'application/x-www-forms-urlencoded'
            }
        }
        self.access_token = requests.post(TOKEN_URL, data).json()['access_token']


