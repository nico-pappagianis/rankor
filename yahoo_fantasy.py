import requests
from http import HTTPStatus
from auth import Auth
import untangle
import os
import _pickle
from urllib.parse import urljoin

AUTHORIZATION = 'Authorization'
BEARER_AUTH_FMT = 'Bearer {token}'
YAHOO_API_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/'

class FantasyData(object):
    auth = Auth()

    def __init__(self, api_query, data_dir, data_file):
        self._api_query = api_query
        self._data_dir = data_dir
        self._data_file = os.path.join(data_dir, data_file)
        self.data = None

    def get(self):
        if not self.data and not self.load():
            self.download()
            # self.save()
        return self.data

    def download(self):
        self.data = self._get()

    def save(self):
        os.makedirs(self._data_dir, exist_ok=True)
        with open(self._data_file, 'wb') as data_file:
            _pickle.dump(self.data, data_file)

    def load(self):
        if os.path.exists(self._data_file):
            self.data = _pickle.load(open(self._data_file, 'rb'))
            return True
        return False

    def _get(self, retry=True):
        query = urljoin(YAHOO_API_URL, self._api_query)
        res = requests.get(query, params={'format': 'xml'}, headers=self.headers())

        if retry and res.status_code == HTTPStatus.UNAUTHORIZED:
            self.auth.refresh_access_token()
            return self._get(retry=False)

        return untangle.parse(res.text)

    def headers(self):
        return {AUTHORIZATION: BEARER_AUTH_FMT.format(token=self.auth.access_token)}
