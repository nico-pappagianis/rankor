import functools
import json
import os
import pickle
import http
from urllib.parse import urljoin

import requests
import untangle

from auth import Auth

AUTHORIZATION = 'Authorization'
BEARER_AUTH_FMT = 'Bearer {token}'
YAHOO_API_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/'


class FantasyData(object):
    auth = Auth()

    def __init__(self, api_query):
        self.data = None
        self._api_query = api_query
        self.download()

    def get_attribute(self, attr, *args):
        return get_attribute(self.data, attr, args)

    def download(self):
        self.data = self._get()

    def _get(self, retry=True):
        query = urljoin(YAHOO_API_URL, self._api_query)
        res = requests.get(query, params={'format': 'xml'}, headers=self.headers())

        if retry and res.status_code == http.HTTPStatus.UNAUTHORIZED:
            self.auth.refresh_access_token()
            return self._get(retry=False)

        return untangle.parse(res.text)

    def headers(self):
        return {AUTHORIZATION: BEARER_AUTH_FMT.format(token=self.auth.access_token)}


def save(obj, dirname, filename):
    os.makedirs(dirname, exist_ok=True)
    path = os.path.join(dirname, filename)
    with open(path, 'wb') as data_file:
        pickle.dump(obj, data_file)


def load(path):
    if os.path.exists(path):
        return pickle.load(open(path, 'rb'))
    return None


def get_attribute(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split('.'))
