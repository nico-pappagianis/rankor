var express = require('express');
var router = express.Router();
var querystring = require('querystring');
require('request-to-curl')
var auth = require('../auth');
var request = require('request');

router.get('/', function (req, res, next) {
    res.redirect('/rankings');
    // var authUrl = 'https://api.login.yahoo.com/oauth2/request_auth';
    //     //?client_id=dj0yJmk9ak5IZ2x5WmNsaHp6JmQ9WVdrOVNqQkJUMnRYTjJrbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD1hYQ--&redirect_uri=oob&response_type=code&language=en-us\n' +
    // const authData = querystring.stringify({
    //     client_id: KEY,
    //     response_type: 'code',
    //     redirect_uri: 'myapp.com'
    // });
    //
    // var options = {
    //     url: authUrl,
    //     json: true,
    //     body: authData
    // };
    //
    // request.get(options, function (err, res, body) {
    //     console.log(res);
    // });
    //
    // auth.getAccessToken(function (tokenData) {
    //     console.log(router.stack);
    //     res.cookie(ACCESS_TOKEN, tokenData[ACCESS_TOKEN]);
    //     res.render('setup');
    // });
});

module.exports = router;
