from pycsp3 import *

# Double round-robin timetable for the 9 teams of the 1997/98 Atlantic Coast Conference
# (Clemson, Duke, FSU, Georgia Tech, Maryland, UNC, NC State, Virginia, Wake Forest) over 18 dates.
# Team indices: 0 Clem, 1 Duke, 2 FSU, 3 GT, 4 UMD, 5 UNC, 6 NCSt, 7 UVA, 8 Wake.
# Date indices: 0 to 17 (date d+1 in the statement). Even indices are weekday fixtures, odd indices
# are weekend fixtures. where: 0 home, 1 bye, 2 away.

n_days = data.n_days
n_teams = data.n_teams
T = range(n_teams)
D = range(n_days)

# plays[d][i][j] = 1 iff team i plays team j on date d (symmetric, zero on the diagonal)
plays = VarArray(size=[n_days, n_teams, n_teams], dom={0, 1})
# hosts[d][i][j] = 1 iff team i is at home against team j on date d
hosts = VarArray(size=[n_days, n_teams, n_teams], dom={0, 1})
# home, away and bye flags of each team on each date (exactly one of them is 1)
home = VarArray(size=[n_days, n_teams], dom={0, 1})
away = VarArray(size=[n_days, n_teams], dom={0, 1})
bye = VarArray(size=[n_days, n_teams], dom={0, 1})

# config[d][i] is the team that team i plays on date d, or i itself on a bye
config = VarArray(size=[n_days, n_teams], dom=range(n_teams))
# where[d][i]: 0 home, 1 bye, 2 away
where = VarArray(size=[n_days, n_teams], dom={0, 1, 2})

# rival of each team (None for FSU), used on the last date
rival = {0: 3, 1: 5, 3: 0, 4: 7, 5: 1, 6: 8, 7: 4, 8: 6}
FSU = 2
UNC, DUKE, WAKE = 5, 1, 8

satisfy(
    # a team does not play itself, and every pairing of two teams is symmetric
    [plays[d][i][i] == 0 for d in D for i in T],
    [hosts[d][i][i] == 0 for d in D for i in T],
    [plays[d][i][j] == plays[d][j][i] for d in D for i in T for j in T if i < j],
    # each team plays at most one opponent on a date, and has a bye when it plays nobody
    [Sum(plays[d][i]) + bye[d][i] == 1 for d in D for i in T],
    # each pair of teams plays once at home and once away over the 18 dates
    [Sum(hosts[d][i][j] for d in D) == 1 for i in T for j in T if i != j],
    # the two teams of a pair play each other twice in total
    [Sum(plays[d][i][j] for d in D) == 2 for i in T for j in T if i < j],
    # exactly one of the two teams of a game is the host
    [hosts[d][i][j] + hosts[d][j][i] == plays[d][i][j] for d in D for i in T for j in T if i < j],
    # a team at home on a date hosts its opponent, away means the opponent hosts it
    [home[d][i] == Sum(hosts[d][i]) for d in D for i in T],
    # every team is home, away or on a bye on each date
    [home[d][i] + away[d][i] + bye[d][i] == 1 for d in D for i in T],
    # the opponent of team i on date d is recorded in config, and i itself on a bye
    [config[d][i] == Sum(j * plays[d][i][j] for j in T) + i * bye[d][i] for d in D for i in T],
    # where: 0 for home, 2 for away, 1 for a bye
    [where[d][i] == 2 - 2 * home[d][i] - bye[d][i] for d in D for i in T],

    # Mirroring. The dates are grouped into pairs (r1, r2) such that each team plays the same team
    # on dates r1 and r2 (the Nemhauser and Trick scheme, 0-based)
    [plays[r1][i][j] == plays[r2][i][j]
     for (r1, r2) in [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (9, 16), (10, 17)]
     for i in T for j in T],

    # No Two Final Aways. No team can play away on both last dates
    [away[n_days - 2][i] + away[n_days - 1][i] <= 1 for i in T],

    # Home/Away/Bye Pattern Constraints. No team may have more than two away matches in a row
    [Sum(away[d + k][i] for k in range(3)) <= 2 for d in range(n_days - 2) for i in T],
    # No team may have more than two home matches in a row
    [Sum(home[d + k][i] for k in range(3)) <= 2 for d in range(n_days - 2) for i in T],
    # No team may have more than three away matches or byes in a row
    [Sum(away[d + k][i] + bye[d + k][i] for k in range(4)) <= 3 for d in range(n_days - 3) for i in T],
    # No team may have more than four home matches or byes in a row
    [Sum(home[d + k][i] + bye[d + k][i] for k in range(5)) <= 4 for d in range(n_days - 4) for i in T],

    # Weekend Pattern. Of the weekends, each team plays four at home, four away, and one bye
    [Sum(home[d][i] for d in range(1, n_days, 2)) == 4 for i in T],
    [Sum(away[d][i] for d in range(1, n_days, 2)) == 4 for i in T],
    [Sum(bye[d][i] for d in range(1, n_days, 2)) == 1 for i in T],

    # First Weekends. Each team must have home matches or byes at least on two of the first five weekends
    [Sum(home[d][i] + bye[d][i] for d in range(1, 10, 2)) >= 2 for i in T],

    # Rival Matches. In the last date, every team except FSU plays against its rival, unless it plays
    # against FSU or has a bye
    [plays[n_days - 1][i][rival[i]] + plays[n_days - 1][i][FSU] + bye[n_days - 1][i] == 1
     for i in T if i != FSU],

    # Constrained Matches. The following pairings must occur at least once in dates 11 to 18
    [Sum(plays[d][WAKE][UNC] for d in range(10, n_days)) >= 1],
    [Sum(plays[d][WAKE][DUKE] for d in range(10, n_days)) >= 1],
    [Sum(plays[d][3][UNC] for d in range(10, n_days)) >= 1],
    [Sum(plays[d][3][DUKE] for d in range(10, n_days)) >= 1],

    # Opponent Sequence Constraints. No team plays in two consecutive dates away against UNC and Duke
    [hosts[d][UNC][i] + hosts[d + 1][DUKE][i] <= 1 for d in range(n_days - 1) for i in T if i not in (UNC, DUKE)],
    [hosts[d][DUKE][i] + hosts[d + 1][UNC][i] <= 1 for d in range(n_days - 1) for i in T if i not in (UNC, DUKE)],
    # No team plays in three consecutive dates against UNC, Duke and Wake (independent of home/away)
    [plays[d][i][a] + plays[d + 1][i][b] + plays[d + 2][i][c] <= 2
     for d in range(n_days - 2) for i in T if i not in (UNC, DUKE, WAKE)
     for (a, b, c) in [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                       (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]],

    # Other Constraints. UNC plays its rival Duke in the last date, and in date 11
    plays[n_days - 1][UNC][DUKE] == 1,
    plays[10][UNC][DUKE] == 1,
    # UNC plays Clem in the second date
    plays[1][UNC][0] == 1,
    # Duke has a bye in date 16
    bye[15][DUKE] == 1,
    # Wake does not play home in date 17
    home[16][WAKE] == 0,
    # Wake has a bye in the first date
    bye[0][WAKE] == 1,
    # Clem, Duke, UMD and Wake do not play away in the last date
    [away[n_days - 1][t] == 0 for t in (0, DUKE, 4, WAKE)],
    # Clem, FSU, GT and Wake do not play away in the first date
    [away[0][t] == 0 for t in (0, FSU, 3, WAKE)],
    # Neither FSU nor NCSt have a bye in the last date
    bye[n_days - 1][FSU] == 0,
    bye[n_days - 1][6] == 0,
    # UNC does not have a bye in the first date
    bye[0][UNC] == 0,
)
