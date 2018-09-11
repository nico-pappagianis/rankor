module.exports.getCurrentWeekMatchups = function (data) {
    return data.fantasy_content.league.scoreboard.matchups.matchup;
};

module.exports.getNumTeams = function (data) {
    return data.fantasy_content.league.num_teams;
};

