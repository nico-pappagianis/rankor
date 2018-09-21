from league import League
import rankings


l = League('nfl', '2018', '1067871')
r = rankings.LeagueRankings(l)
r.rank()
print(l)