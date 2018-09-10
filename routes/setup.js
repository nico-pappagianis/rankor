var express = require('express');
var router = express.Router();
var request = require('request');
var parser = require('fast-xml-parser');
var query = require('../query');
var format = require('string-format');
var random = require('../public/javascripts/random');

const GAME_CODES_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/games;game_codes=nfl;seasons={}';

router.post('/season', function (req, res, next) {
    const season = req.body['season'];
    res.cookie('season', season);
    var options = {
        url: format(GAME_CODES_URL, season),
        headers: {
            Authorization: 'Bearer ' + req.cookies[ACCESS_TOKEN]
        }
    };

    query.query(options, function (data) {
        if (data[ACCESS_TOKEN]) {
            res.cookie(ACCESS_TOKEN, data[ACCESS_TOKEN]);
            return res.redirect('setup/season');
        }
        else {
            res.cookie(GAME_KEY, data.fantasy_content.games.game.game_key);
            return res.redirect('/rankings')
        }
    });

});

router.get('/season', function (req, res, next) {
    var numTeams = 12;
    var minAvg = 120;
    var maxAvg = 150;
    var stdDev = 1;
    var avgStep = Math.abs(maxAvg - minAvg) / numTeams;
    res.render('setup', {
        numTeams: numTeams,
        minAvg: minAvg,
        maxAvg: maxAvg,
        stdDev: stdDev})
});

router.get('/manual', function (req, res, next) {
    var numTeams = parseInt(req.body.numTeams) || 12;
    var minAvg = parseInt(req.body.minAvg) || 120;
    var maxAvg = parseInt(req.body.maxAvg) || 150;
    var stdDev = parseInt(req.body.stdDev) || 1;

    var winValue = parseInt(req.body.winValue) || 10;
    var outscoreValue = parseInt(req.body.outscoreValue) || 1;
    var drawValue = parseInt(req.body.drawValue) || 5;
    res.render('setup', {
        numTeams: numTeams,
        winValue: winValue,
        outscoreValue: outscoreValue,
        drawValue: drawValue,
        minAvg: minAvg,
        maxAvg: maxAvg,
        stdDev: stdDev
    });
});

router.post('/manual', function (req, res, next) {
    var numTeams = parseInt(req.body.numTeams) || 12;
    var minAvg = parseInt(req.body.minAvg) || 120;
    var maxAvg = parseInt(req.body.maxAvg) || 150;
    var stdDev = parseInt(req.body.stdDev) || 1;
    var avgStep = Math.abs(maxAvg - minAvg) / numTeams;

    var winValue = parseInt(req.body.winValue) || 10;
    var outscoreValue = parseInt(req.body.outscoreValue) || 1;
    var drawValue = parseInt(req.body.drawValue) || 5;

    var seasonPoints = {};
    for (weekIndex = 1; weekIndex <= 14; weekIndex++) {
        seasonPoints[weekIndex] = {};
        for (t = 1; t <= numTeams; t++) {
            seasonPoints[weekIndex][t] = Math.round(random.gaussian(minAvg + Math.max(1, avgStep) * t, stdDev)());
        }
    }

    var rankedSeasonPoints = toKVArray(seasonPoints);

    var initialzer = {};
    for (i = 1; i <= numTeams; i++) {
        initialzer[i] = 0;
    }

    var wins = {...initialzer};
    var outscores = {...initialzer};
    var draws = {...initialzer};

    var matchups = {};
    for (let weekIndex = 0; weekIndex < 14; weekIndex++) {
        var weekNum = weekIndex + 1;
        matchups[weekNum] = [];

        var bagOfTeams = Array.from(Array(numTeams).keys());

        while (bagOfTeams.length !== 0) {

            var opp1 = Math.floor(Math.random() * bagOfTeams.length);
            opp1 = bagOfTeams.splice(opp1, 1)[0];

            var opp2 = Math.floor(Math.random() * bagOfTeams.length);
            opp2 = bagOfTeams.splice(opp2, 1)[0];

            opp1++;
            opp2++;

            matchups[weekNum].push({opp1: opp1, opp2: opp2});

            rankedSeasonPoints[weekNum].rankings[opp1].wins = 0;
            rankedSeasonPoints[weekNum].rankings[opp2].wins = 0;
            rankedSeasonPoints[weekNum].rankings[opp1].outscores = 0;
            rankedSeasonPoints[weekNum].rankings[opp2].outscores = 0;
            rankedSeasonPoints[weekNum].rankings[opp1].draws = 0;
            rankedSeasonPoints[weekNum].rankings[opp2].draws = 0;
            if (rankedSeasonPoints[weekNum].rankings[opp1].points > rankedSeasonPoints[weekNum].rankings[opp2].points) {
                wins[opp1]++;
                rankedSeasonPoints[weekNum].rankings[opp1].wins = 1;

                let opp1Outscores = numTeams - rankedSeasonPoints[weekNum].rankings[opp1].rank - 1;
                outscores[opp1] += opp1Outscores;
                rankedSeasonPoints[weekNum].rankings[opp1].outscores = opp1Outscores;

                let opp2Outscores = numTeams - rankedSeasonPoints[weekNum].rankings[opp2].rank;
                outscores[opp2] += opp2Outscores;
                rankedSeasonPoints[weekNum].rankings[opp2].outscores = opp2Outscores;
            }
            else if (rankedSeasonPoints[weekNum].rankings[opp2].points > rankedSeasonPoints[weekNum].rankings[opp1].points) {
                wins[opp2]++;
                rankedSeasonPoints[weekNum].rankings[opp2].wins = 1;

                let opp2Outscores = numTeams - rankedSeasonPoints[weekNum].rankings[opp2].rank - 1;
                outscores[opp2] += opp2Outscores;
                rankedSeasonPoints[weekNum].rankings[opp2].outscores = opp2Outscores;

                let opp1Outscores = numTeams - rankedSeasonPoints[weekNum].rankings[opp1].rank;
                outscores[opp1] += opp1Outscores;
                rankedSeasonPoints[weekNum].rankings[opp1].outscores = opp1Outscores;
            }
            else {
                draws[opp1]++;
                draws[opp2]++;
                rankedSeasonPoints[weekNum].rankings[opp1].draws = 1;
                rankedSeasonPoints[weekNum].rankings[opp2].draws = 1;
            }
        }
        bagOfTeams = Array.from(Array(numTeams).keys());
    }
    var totals = {};
    for (var i = 1; i <= numTeams; i++) {
        totals[i] = wins[i] * winValue + outscores[i] * outscoreValue + draws[i] * drawValue;
    }

    res.render('setup', {
        matchups: matchups,
        rankedSeasonPoints: rankedSeasonPoints,
        numTeams: numTeams,
        wins: wins,
        outscores: outscores,
        draws: draws,
        winValue: winValue,
        outscoreValue: outscoreValue,
        drawValue: drawValue,
        totals: totals,
        minAvg: minAvg,
        maxAvg: maxAvg,
        stdDev: stdDev
    });
});

function toKVArray(seasonPoints) {

    var sortedSeasonPointsArr = [];

    for (var weekIndex in seasonPoints) {
        var weekPoints = seasonPoints[weekIndex];

        var teamPoints = [];
        for (var team in weekPoints) {
            teamPoints.push([team, weekPoints[team]])
        }

        teamPoints.sort(function compare(kv1, kv2) {
            // This comparison function has 3 return cases:
            // - Negative number: kv1 should be placed BEFORE kv2
            // - Positive number: kv1 should be placed AFTER kv2
            // - Zero: they are equal, any order is ok between these 2 items
            return kv1[1] - kv2[1]
        });
        teamPoints.reverse();
        sortedSeasonPointsArr.push(teamPoints);
    }

    var sortedSeasonPoints = {};
    for (let weekIndex = 0; weekIndex < sortedSeasonPointsArr.length; weekIndex++) {
        var weekNum = weekIndex + 1;
        var weekName = 'Week ' + weekNum;

        var week = {};
        week.number = weekNum;
        week.name = weekName;
        week.rankings = {};

        for (let i = 0; i < sortedSeasonPointsArr[i].length; i++) {
            var teamNumber = sortedSeasonPointsArr[weekIndex][i][0];
            week.rankings[teamNumber] = {
                teamName: 'Team ' + teamNumber,
                teamNumber: teamNumber,
                points: sortedSeasonPointsArr[weekIndex][i][1],
                rank: i + 1
            };
        }
        sortedSeasonPoints[weekNum] = week;
    }
    return sortedSeasonPoints;
}

module.exports = router;
