var express = require('express');
var router = express.Router();
var parser = require('fast-xml-parser');
var query = require('../query');
var format = require('string-format');


global.GAME_KEY = 'game_key';
global.LEAGUE_KEY = '1067871';
global.SEASON_DATA = 'season_data';

// LEAGUE_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}.l.{}';
LEAGUE_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/league/380.l.1067871/scoreboard';

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

    query.query(options, function (data) {
        res.cookie(SEASON_DATA, data);
        getResultsForCurrentWeek(data);
    });
});

function getCurrentWeekMatchups(data) {
    return data.fantasy_content.league.scoreboard.matchups.matchup;
}

function getNumTeams(data) {
    return data.fantasy_content.league.num_teams;
}

function getResultsForCurrentWeek(data) {
    let results = [];
    let matchups = getCurrentWeekMatchups(data);
    let numTeams = getNumTeams(data);

    for (let i = 0; i < matchups.length; i++) {
        let teams = matchups[i].teams.team;

        let team1Id = teams[0].team_id;
        let team1Points = teams[0].team_points.total;
        let team2Id = teams[1].team_id;
        let team2Points = teams[1].team_points.total;

        results.push({
                teamId: team1Id,
                points: team1Points,
                win: team1Points > team2Points,
                draw: team1Points === team2Points,
                opponentId: team2Id
            }
        );
        results.push({
                teamId: team2Id,
                points: team2Points,
                win: team2Points > team1Points,
                draw: team2Points === team1Points,
                opponentId: team1Id
            }
        );
    }

    results.sort(function compare(kv1, kv2) {
        return kv2.points - kv1.points;
    });

    let nextRank = 1;
    for (let i = 0; i < results.length; i++) {

        if (results[i].draw) {
            results[i].rank = nextRank;
            results[findMatchupIndexForTeamId(results[i].opponentId)].rank = nextRank;
            nextRank++;
        }
        else {
            results[i].rank = nextRank++;
        }

        results[i].outscores = results[i].win ? numTeams - results[i].rank - 1 : numTeams - results[i].rank;
        results[i].rankingPoints = results[i].win * 10 + results[i].outscores * 1 + results[i].draw * 5;
    }
    return results;
}


function findMatchupIndexForTeamId(id, results) {
    for (let i = 0; i < results.length; i++) {
        if (results[i].teamId === id) {
            return i;
        }
    }
}

module.exports = router;
