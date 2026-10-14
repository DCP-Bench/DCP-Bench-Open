"""ACC basketball schedule (CSPLib 11): a double round-robin timetable for the nine teams of
the 1997/98 Atlantic Coast Conference over 18 dates (odd dates weekdays, even dates
weekends), with mirroring, home/away/bye pattern, weekend, rival, constrained-match,
opponent-sequence and team-specific rules.

The model reports config[d][i], the opponent of team i on day d (i itself for a bye), and
where[d][i]: 0 home, 1 bye, 2 away.
"""
import pulp


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]
    teams = range(n_teams)
    days = range(n_days)

    # The team names, rivals and mirroring scheme belong to the problem statement and are
    # mirrored from the reference.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = range(9)
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]
    scheme = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
    weekends = [d for d in days if d % 2 == 1]
    HOME, BYE, AWAY = 0, 1, 2

    problem = pulp.LpProblem("acc_basketball_schedule", pulp.LpMinimize)  # satisfaction

    # host[d][i][j] = 1 if team i plays team j at home on day d (so j plays away);
    # bye[d][i] = 1 if team i does not play on day d
    host = [[[pulp.LpVariable(f"host_{d}_{i}_{j}", cat="Binary") if i != j else None
              for j in teams] for i in teams] for d in days]
    bye = [[pulp.LpVariable(f"bye_{d}_{i}", cat="Binary") for i in teams] for d in days]

    def plays(d, i, j):
        """1 if teams i and j meet on day d (whoever is at home); for i == j, a bye."""
        if i == j:
            return bye[d][i]
        return host[d][i][j] + host[d][j][i]

    def home(d, i):
        return pulp.lpSum(host[d][i][j] for j in teams if j != i)

    def away(d, i):
        return pulp.lpSum(host[d][j][i] for j in teams if j != i)

    # a team has one opponent (or a bye) each day; meetings are mutual by construction,
    # so no two teams share an opponent on the same day
    for d in days:
        for i in teams:
            problem += home(d, i) + away(d, i) + bye[d][i] == 1

    # double round-robin: each team plays each other team once at home (and so once away)
    for i in teams:
        for j in teams:
            if i != j:
                problem += pulp.lpSum(host[d][i][j] for d in days) == 1

    # 1. Mirroring: dates d and scheme[d] have the same pairings with home and away swapped
    for d in days:
        e = scheme[d]
        for i in teams:
            problem += bye[d][i] == bye[e][i]
            for j in teams:
                if i != j:
                    problem += host[d][i][j] == host[e][j][i]

    # 2. No team plays away on both last dates
    for i in teams:
        problem += away(n_days - 2, i) + away(n_days - 1, i) <= 1

    # 3. Home/away/bye patterns
    for i in teams:
        for d in range(n_days - 2):
            # no more than two home matches in a row
            problem += pulp.lpSum(home(d + k, i) for k in range(3)) <= 2
            # no more than two away matches in a row
            problem += pulp.lpSum(away(d + k, i) for k in range(3)) <= 2
        for d in range(n_days - 3):
            # no more than three away matches or byes in a row
            problem += pulp.lpSum(away(d + k, i) + bye[d + k][i] for k in range(4)) <= 3
        for d in range(n_days - 4):
            # no more than four home matches or byes in a row
            problem += pulp.lpSum(home(d + k, i) + bye[d + k][i] for k in range(5)) <= 4

    # 4. Of the weekends, each team plays four at home, four away, and has one bye
    for i in teams:
        problem += pulp.lpSum(home(d, i) for d in weekends) == 4
        problem += pulp.lpSum(away(d, i) for d in weekends) == 4
        problem += pulp.lpSum(bye[d][i] for d in weekends) == 1

    # 5. Each team has home matches or byes on at least two of the first five weekends
    for i in teams:
        problem += pulp.lpSum(home(d, i) + bye[d][i] for d in weekends[:5]) >= 2

    # 6. On the last date every team except FSU plays its rival, unless it plays FSU or
    #    has a bye: every other opponent is ruled out
    last = n_days - 1
    for i in teams:
        if i != FSU:
            for j in teams:
                if j not in (rivals[i], FSU, i):
                    problem += plays(last, i, j) == 0

    # 7. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each meet at least once in dates 11 to 18
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        problem += pulp.lpSum(plays(d, a, b) for d in range(10, n_days)) >= 1

    # 8. Opponent sequences
    for t in teams:
        if t not in (DUKE, UNC):
            # no team plays away against UNC and then away against Duke on consecutive
            # dates, or the other way round
            for d in range(n_days - 1):
                problem += host[d][UNC][t] + host[d + 1][DUKE][t] <= 1
                problem += host[d][DUKE][t] + host[d + 1][UNC][t] <= 1
        if t not in (UNC, DUKE, WAKE):
            # no team plays UNC, Duke and Wake on three consecutive dates, in any order
            orders = [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                      (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]
            for d in range(n_days - 2):
                for a, b, c in orders:
                    problem += plays(d, t, a) + plays(d + 1, t, b) + plays(d + 2, t, c) <= 2

    # 9. Other constraints
    problem += plays(10, UNC, DUKE) == 1     # UNC plays its rival Duke in date 11
    problem += plays(last, UNC, DUKE) == 1   # and in the last date
    problem += plays(1, UNC, CLEM) == 1      # UNC plays Clem in the second date
    problem += bye[15][DUKE] == 1            # Duke has a bye in date 16
    problem += home(16, WAKE) == 0           # Wake does not play home in date 17
    problem += bye[0][WAKE] == 1             # Wake has a bye in the first date
    for t in (CLEM, DUKE, UMD, WAKE):        # these do not play away in the last date
        problem += away(last, t) == 0
    for t in (CLEM, FSU, GT, WAKE):          # these do not play away in the first date
        problem += away(0, t) == 0
    for t in (FSU, NCSt):                    # neither has a bye in the last date
        problem += bye[last][t] == 0
    problem += bye[0][UNC] == 0              # UNC does not have a bye in the first date

    # the opponent of each team each day, and whether it is home (0), bye (1) or away (2)
    config = [[pulp.lpSum(j * plays(d, i, j) for j in teams) for i in teams] for d in days]
    where = [[HOME * home(d, i) + BYE * bye[d][i] + AWAY * away(d, i) for i in teams]
             for d in days]
    return problem, {"config": config, "where": where}
