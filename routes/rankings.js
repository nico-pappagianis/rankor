var express = require('express');
var router = express.Router();
var parser = require('fast-xml-parser');
var query = require('../query');
var format = require('string-format');
var fs = require('fs');
var util = require('util');
var WeekResults = require('../public/javascripts/results').WeekResults;

global.GAME_KEY = 'game_key';
global.LEAGUE_KEY = '1067871';
global.SEASON_DATA = 'season_data';

// LEAGUE_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}.l.{}';
var LEAGUE_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/league/380.l.1067871/scoreboard';
var weekResults;

router.post('/', function (req, res, next) {
    console.log(req);
});

router.get('/', function (req, res, next) {
    const options = {
        url: LEAGUE_URL,
        headers: {
            Authorization: 'Bearer ' + req.cookies[ACCESS_TOKEN]
        }
    };
    try {
        weekResults = JSON.parse(fs.readFileSync('./weekResults.js', 'utf8'));
        res.render('rankings', {weekResults: weekResults});
    }
    catch (error) {
        query.query(options, function (data) {
            weekResults = new WeekResults(data);
            fs.writeFile('./weekResults.js', JSON.stringify(weekResults), function (err) {
                if (err) console.log(err)
            });
            res.redirect('/');
        });

    }

});


module.exports = router;
