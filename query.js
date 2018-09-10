var request = require('request');
var parser = require('fast-xml-parser');
var auth = require('./auth');

global.FANTASY_CONTENT = 'fantasy_content';

module.exports.query = function (options, callback) {
    request.get(options, function (err, res, body) {
        var data = parser.parse(body);

        if (data['yahoo:error']['yahoo:description'].includes('token_rejected')) {
            return auth.getAccessToken(function (token) {
                options.headers.Authorization = 'Bearer ' + token;
                request.get(options, function (err, res, body) {
                    return callback(parser.parse(body));
                });
            });
        }
        else {
            return callback(data);
        }
    });
};



