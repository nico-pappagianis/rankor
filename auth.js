var querystring = require('querystring');
var request = require('request');
var url = require('url');

global.ACCESS_TOKEN = 'ACCESS_TOKEN';
global.KEY = 'dj0yJmk9YjBUTFJqTWRRTDNrJmQ9WVdrOU5qWkVja3RrTXpBbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1jYg--';
global.SECRET = 'b4293f4f33f0c4fbd94fe35e1a538f30aeffcb62';
const REFRESH_TOKEN = 'AOrIhFvw9XDqC4c89LQTjDa8omlRKUw3CT9asqf_RD2j9BywrjVJeMPyNrVp3nfeLFM-';

const YAHOO_AUTH_URL = 'https://api.login.yahoo.com/oauth2/';
const TOKEN_URL = url.resolve(YAHOO_AUTH_URL, 'get_token');
const BASIC_AUTH = 'Basic ' + new Buffer(KEY + ':' + SECRET).toString('base64');

const refreshTokenData = querystring.stringify({
    refresh_token: REFRESH_TOKEN,
    grant_type: 'refresh_token',
    redirect_uri: 'oob',
    code: '9hvuzj8'
});

const options = {
    url: TOKEN_URL,
    method: 'POST',
    body: refreshTokenData,
    json: true,
    headers: {
        Authorization: BASIC_AUTH,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
};

module.exports.getAccessToken = function getAccessToken(callback) {
    request.post(
        options,
        (err, res, body) => {
            return callback(body['access_token'])
        });
};





