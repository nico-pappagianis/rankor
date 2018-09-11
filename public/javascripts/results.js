var ffparser = require('./ffparser');


var WeekResults = function (fantasyData) {

    this.results = getResultsForCurrentWeek(fantasyData);
    this.getResultsForTeamId = function(id) {
        return getResultsForTeamId(id, this.results);
    };
    this.weekNumber = fantasyData.fantasy_content.league.scoreboard.week;
    this.weekName = 'Week ' + this.weekNumber;

    function getResultsForCurrentWeek(data) {
        let results = {};
        results['overall'] = [];
        results['matchups'] = [];
        let matchups = ffparser.getCurrentWeekMatchups(data);
        let numTeams = ffparser.getNumTeams(data);

        for (let i = 0; i < matchups.length; i++) {
            let teams = matchups[i].teams.team;
            let team1Id = teams[0].team_id;
            let team1Points = teams[0].team_points.total;
            let team2Id = teams[1].team_id;
            let team2Points = teams[1].team_points.total;

            let team1Results = {
                teamId: team1Id,
                points: team1Points,
                win: team1Points > team2Points,
                draw: team1Points === team2Points,
                opponentId: team2Id,
                name: teams[0].name
            };

            let team2Results = {
                teamId: team2Id,
                points: team2Points,
                win: team2Points > team1Points,
                draw: team2Points === team1Points,
                opponentId: team1Id,
                name: teams[1].name
            };
            results.overall.push(team1Results, team2Results);
            results.matchups.push([team1Results, team2Results]);
        }

        let overall = results.overall; 
        overall.sort(function compare(kv1, kv2) {
            return kv2.points - kv1.points;
        });

        let nextRank = 1;
        for (let i = 0; i < overall.length; i++) {

            if (overall[i].draw) {
                overall[i].rank = nextRank;
                overall[getIndexForTeamId(overall[i].opponentId)].rank = nextRank;
                nextRank++;
            }
            else {
                overall[i].rank = nextRank++;
            }

            overall[i].outscores = overall[i].win ? numTeams - overall[i].rank - 1 : numTeams - overall[i].rank;
            overall[i].rankingPoints = overall[i].win * 10 + overall[i].outscores * 1 + overall[i].draw * 5;
        }
        return results;
    }


    function getIndexForTeamId(id, results) {
        for (let i = 0; i < results.length; i++) {
            if (results[i].teamId === id) {
                return i;
            }
        }
    }

    function getResultsForTeamId(id, results) {
        return results[getIndexForTeamId(id, results)];

    }
};

module.exports.WeekResults = WeekResults;