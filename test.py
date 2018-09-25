from league import League
import rankings


l = League('nfl', '2018', '1067871')
r = rankings.LeagueRankings(l, 10, 5, 1)
print(l)