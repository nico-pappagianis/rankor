function update() {
    last_updated = moment().tz(PST).format(TIME_FORMAT);

    if (!week_in_progress) {
        return false;
    }

    $.getJSON($SCRIPT_ROOT + '/update_in_progress_games', {
        league_data_path: league_data_path
    }, function (data) {
        if (data === "null") {
            return false;
        }
        let rankings = JSON.parse(data);
        let current_week = rankings.league.current_week;
        rankings.week_ranks[current_week].forEach(rank => {
            let id_prefix = '#' + [current_week, rank.team.team_id, rank.opponent.team_id].join('-') + '-';
            $(id_prefix + 'rank').text(rank.rank);
            $(id_prefix + 'team-name').text(rank.team.name);
            $(id_prefix + 'team-points').text(rank.team_points);
            $(id_prefix + 'opponent-points').text(rank.opponent_points);
            $(id_prefix + 'opponent-name').text(rank.opponent.name);
        });
        rankings.sorted_season_ranks_in_progress.forEach(rank => {
            rank = rank[1];
            let id_prefix = '#season-rank-progress-' + rank.overall_rank + '-';
            $(id_prefix + 'team-name').text(rank.team.name);
            $(id_prefix + 'ranking-points').text(rank.ranking_points);
            $(id_prefix + 'record').text(rank.wins + '-' + rank.losses + (rank.draws ? ('-' + rank.draws) : ''));
            $(id_prefix + 'avg-rank').text(Number((rank.avg_rank).toFixed(1)));
            $(id_prefix + 'outscores').text(rank.outscores);
            $(id_prefix + 'avg-outscores').text(Number((rank.avg_outscores).toFixed(1)));
        });
        return true;
    });

    $("#updated").text(last_updated);
    return true;
}

$(document).ready(() => {
    setInterval(update, 30000)
});

