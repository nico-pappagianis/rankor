function compare(comparisonStandings) {
    let startWeek = comparisonStandings[0][1];
    let endWeek = comparisonStandings[1][1];
    let startWeekStandings = comparisonStandings[0][0];
    let endWeekStandings = comparisonStandings[1][0];

    $("#standings-comparison-title-output").text("Week " + startWeek + "&Delta" +  "Week " + endWeek );


    startWeekStandings.forEach(function (teamRanking) {
        let ranking = teamRanking[1];
        let rank = ranking.overall_rank;
        $("#start-week-" + rank + "-overall-rank").text(rank);
        $("#start-week-" + rank + "-team-name").text(ranking.team.name);
        $("#start-week-" + rank + "-ranking-points").text(ranking.ranking_points);
        $("#start-week-" + rank + "-record").text(ranking.wins - ranking.losses + (ranking.draws ? "-" + ranking.draws : ""));
    });
    
    endWeekStandings.forEach(function (teamRanking) {
        let ranking = teamRanking[1];
        let rank = ranking.overall_rank;
        $("#end-week-" + rank + "-overall-rank").text(rank);
        $("#end-week-" + rank + "-team-name").text(ranking.team.name);
        $("#end-week-" + rank + "-ranking-points").text(ranking.ranking_points);
        $("#end-week-" + rank + "-record").text(ranking.wins - ranking.losses + (ranking.draws ? "-" + ranking.draws : ""));
    });
}