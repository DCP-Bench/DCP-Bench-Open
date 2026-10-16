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

CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = 0, 1, 2, 3, 4, 5, 6, 7, 8
rival = {CLEM: GT, DUKE: UNC, GT: CLEM, UMD: UVA, UNC: DUKE, NCST: WAKE, UVA: UMD, WAKE: NCST}

# config[d][i] is the team that team i plays on date d, or i itself on a bye
# the mirroring scheme (0-based pairs of dates) makes each team meet the same opponent on both dates of a
# pair, so the paired dates share their config row; only the first date of each pair is a variable
MIRROR = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (9, 16), (10, 17)]
base_dates = [r1 for (r1, r2) in MIRROR]
config_base = VarArray(size=[len(base_dates), n_teams], dom=range(n_teams))
config = [None] * n_days
for k, (r1, r2) in enumerate(MIRROR):
    config[r1] = config_base[k]
    config[r2] = config_base[k]
# where[d][i]: 0 home, 1 bye, 2 away
where = VarArray(size=[n_days, n_teams], dom={0, 1, 2})

# home, away and bye flags of each team on each date, each derived from where
home = VarArray(size=[n_days, n_teams], dom={0, 1})
away = VarArray(size=[n_days, n_teams], dom={0, 1})
bye = VarArray(size=[n_days, n_teams], dom={0, 1})

# hosts[d][i][j] = 1 iff team i is at home against team j on date d (zero when i does not play j)
hosts = VarArray(size=[n_days, n_teams, n_teams], dom={0, 1})

satisfy(
    # a team plays against one opponent or has a bye on each date, and the pairing is symmetric
    [(config[d][i] == j) == (config[d][j] == i) for d in D for i in T for j in T if i < j],

    # a bye is recorded as the team itself in config, and as where 1
    [(where[d][i] == 1) == (config[d][i] == i) for d in D for i in T],

    # each pair of teams meets twice over the 18 dates, and each team has two byes
    [Count([config_base[k][i] for k in range(len(base_dates))], value=j) == 1 for i in T for j in T],

    # the two teams of a game are one at home and one away
    [imply(config[d][i] == j, where[d][i] + where[d][j] == 2) for d in D for i in T for j in T if i != j],

    # the home, away and bye flags follow where
    [Table(scope=[where[d][i], home[d][i]], supports=[(0, 1), (1, 0), (2, 0)]) for d in D for i in T],
    [Table(scope=[where[d][i], away[d][i]], supports=[(0, 0), (1, 0), (2, 1)]) for d in D for i in T],
    [Table(scope=[where[d][i], bye[d][i]], supports=[(0, 0), (1, 1), (2, 0)]) for d in D for i in T],

    # hosts[d][i][j] is 1 exactly when i is home against j on date d
    [Table(scope=[config[d][i], where[d][i], hosts[d][i][j]],
           supports=[(j, 0, 1)] + [(x, w, 0) for x in range(n_teams) for w in range(3) if (x, w) != (j, 0)])
     for d in D for i in T for j in T if i != j],
    # a team does not host itself
    [hosts[d][i][i] == 0 for d in D for i in T],
    # each pair of teams has exactly one home game for each team
    [Sum(hosts[d][i][j] for d in D) == 1 for i in T for j in T if i != j],

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
    [Or(config[n_days - 1][i] == rival[i], config[n_days - 1][i] == FSU, config[n_days - 1][i] == i)
     for i in T if i != FSU],

    # Constrained Matches. The following pairings must occur at least once in dates 11 to 18
    [Or(*[config[d][WAKE] == UNC for d in range(10, n_days)])],
    [Or(*[config[d][WAKE] == DUKE for d in range(10, n_days)])],
    [Or(*[config[d][GT] == UNC for d in range(10, n_days)])],
    [Or(*[config[d][GT] == DUKE for d in range(10, n_days)])],

    # Opponent Sequence Constraints. No team plays in two consecutive dates away against UNC and Duke
    [hosts[d][UNC][i] + hosts[d + 1][DUKE][i] <= 1 for d in range(n_days - 1) for i in T if i not in (UNC, DUKE)],
    [hosts[d][DUKE][i] + hosts[d + 1][UNC][i] <= 1 for d in range(n_days - 1) for i in T if i not in (UNC, DUKE)],
    # No team plays in three consecutive dates against UNC, Duke and Wake (independent of home/away)
    [Or(config[d][i] != a, config[d + 1][i] != b, config[d + 2][i] != c)
     for d in range(n_days - 2) for i in T if i not in (UNC, DUKE, WAKE)
     for (a, b, c) in [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                       (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]],

    # Other Constraints. UNC plays its rival Duke in the last date, and in date 11
    config[n_days - 1][UNC] == DUKE,
    config[10][UNC] == DUKE,
    # UNC plays Clem in the second date
    config[1][UNC] == CLEM,
    # Duke has a bye in date 16
    config[15][DUKE] == DUKE,
    # Wake does not play home in date 17
    where[16][WAKE] != 0,
    # Wake has a bye in the first date
    config[0][WAKE] == WAKE,
    # Clem, Duke, UMD and Wake do not play away in the last date
    [where[n_days - 1][t] != 2 for t in (CLEM, DUKE, UMD, WAKE)],
    # Clem, FSU, GT and Wake do not play away in the first date
    [where[0][t] != 2 for t in (CLEM, FSU, GT, WAKE)],
    # Neither FSU nor NCSt have a bye in the last date
    config[n_days - 1][FSU] != FSU,
    config[n_days - 1][NCST] != NCST,
    # UNC does not have a bye in the first date
    config[0][UNC] != UNC,
)
