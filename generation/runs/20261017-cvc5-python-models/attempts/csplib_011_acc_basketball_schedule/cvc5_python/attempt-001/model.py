# ACC basketball schedule (CSPLib 011), 1997/98 Atlantic Coast Conference.
# Double round-robin of n teams over the dates, with the constraints listed in the problem statement.
# config[d][i] is the opponent of team i on date d, and i itself for a bye.
# where[d][i] is 0 for home, 1 for a bye, 2 for away.
# Teams are 0-based in the order Clemson, Duke, FSU, GT, UMD, UNC, NCSt, UVA, Wake.
# The search runs on Boolean atoms: host[d][i][j] says team i plays at home against j on date d.

import itertools

import cvc5.pythonic as cz

CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}
# Mirroring scheme of Nemhauser and Trick, dates 1-based in the statement.
MIRROR = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]


def build(instance):
    n = instance["n_teams"]
    days = instance["n_days"]

    host = [[[None] * n for _ in range(n)] for _ in range(days)]
    for d in range(days):
        for i in range(n):
            for j in range(n):
                if i != j:
                    host[d][i][j] = cz.Bool(f"host_{d}_{i}_{j}")
    home = [[cz.Bool(f"home_{d}_{i}") for i in range(n)] for d in range(days)]
    away = [[cz.Bool(f"away_{d}_{i}") for i in range(n)] for d in range(days)]
    bye = [[cz.Bool(f"bye_{d}_{i}") for i in range(n)] for d in range(days)]
    config = [[cz.Int(f"config_{d}_{i}") for i in range(n)] for d in range(days)]
    where = [[cz.Int(f"where_{d}_{i}") for i in range(n)] for d in range(days)]

    def play(d, i, j):
        # Teams i and j meet on date d, at home for either of them.
        return cz.Or(host[d][i][j], host[d][j][i])

    def count(terms):
        return cz.Sum([cz.If(t, 1, 0) for t in terms])

    cons = []

    # Each date, a team hosts, visits or has a bye, and at most one of its games is played.
    for d in range(days):
        for i in range(n):
            opponents = [j for j in range(n) if j != i]
            cons.append(home[d][i] == cz.Or(*[host[d][i][j] for j in opponents]))
            cons.append(away[d][i] == cz.Or(*[host[d][j][i] for j in opponents]))
            cons.append(bye[d][i] == cz.Not(cz.Or(home[d][i], away[d][i])))
            games = [host[d][i][j] for j in opponents] + [host[d][j][i] for j in opponents]
            for x, y in itertools.combinations(games, 2):
                cons.append(cz.Not(cz.And(x, y)))

    # Double round-robin: each team plays each other team once at home and once away,
    # so each ordered pair has exactly one home date.
    for i in range(n):
        for j in range(n):
            if i != j:
                dates = [host[d][i][j] for d in range(days)]
                cons.append(cz.Or(*dates))
                for x, y in itertools.combinations(dates, 2):
                    cons.append(cz.Not(cz.And(x, y)))

    # Weekend pattern: each team plays four at home, four away and one bye on the weekends.
    # The weekends are the 0-based odd dates, the 1-based even dates.
    weekends = [d for d in range(days) if d % 2 == 1]
    for i in range(n):
        cons.append(count([home[d][i] for d in weekends]) == 4)
        cons.append(count([away[d][i] for d in weekends]) == 4)
        cons.append(count([bye[d][i] for d in weekends]) == 1)

    # Home/away/bye pattern: no more than two away matches in a row, no more than two home
    # matches in a row, no more than three away matches or byes in a row, and no more than
    # four home matches or byes in a row.
    for i in range(n):
        for d in range(days - 2):
            cons.append(cz.Not(cz.And(away[d][i], away[d + 1][i], away[d + 2][i])))
            cons.append(cz.Not(cz.And(home[d][i], home[d + 1][i], home[d + 2][i])))
        for d in range(days - 3):
            cons.append(cz.Not(cz.And(*[cz.Or(away[d + k][i], bye[d + k][i]) for k in range(4)])))
        for d in range(days - 4):
            cons.append(cz.Not(cz.And(*[cz.Or(home[d + k][i], bye[d + k][i]) for k in range(5)])))

    # First weekends: each team has home matches or byes at least on two of the first five weekends.
    for i in range(n):
        cons.append(count([cz.Or(home[d][i], bye[d][i]) for d in [1, 3, 5, 7, 9]]) >= 2)

    # Mirroring: each team plays the same opponent on the two dates of each mirror pair.
    for a, b in MIRROR:
        for i in range(n):
            cons.append(bye[a - 1][i] == bye[b - 1][i])
            for j in range(n):
                if j != i:
                    cons.append(play(a - 1, i, j) == play(b - 1, i, j))

    # No two final aways: no team plays away on both last dates.
    for i in range(n):
        cons.append(cz.Not(cz.And(away[days - 2][i], away[days - 1][i])))

    # Rival matches: in the last date every team except FSU plays against its rival, unless it
    # plays against FSU or has a bye.
    for i in range(n):
        if i == FSU:
            continue
        cons.append(cz.Or(play(days - 1, i, RIVAL[i]), play(days - 1, i, FSU), bye[days - 1][i]))

    # Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke occur at least once in dates 11 to 18.
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        cons.append(cz.Or(*[play(d, a, b) for d in range(10, days)]))

    # Opponent sequence: no team plays in two consecutive dates away against UNC and Duke.
    for i in range(n):
        if i not in (UNC, DUKE):
            for d in range(days - 1):
                cons.append(cz.Not(cz.And(host[d][UNC][i], host[d + 1][DUKE][i])))
                cons.append(cz.Not(cz.And(host[d][DUKE][i], host[d + 1][UNC][i])))
    # No team plays in three consecutive dates against UNC, Duke and Wake, home or away.
    for i in range(n):
        if i in (UNC, DUKE, WAKE):
            continue
        for d in range(days - 2):
            for x, y, z in itertools.permutations([UNC, DUKE, WAKE]):
                cons.append(cz.Not(cz.And(play(d, i, x), play(d + 1, i, y), play(d + 2, i, z))))

    # Other constraints of the statement, with dates converted from 1-based to 0-based.
    # UNC plays its rival Duke in the last date and in date 11.
    cons.append(play(days - 1, UNC, DUKE))
    cons.append(play(10, UNC, DUKE))
    # UNC plays Clemson in the second date.
    cons.append(play(1, UNC, CLEM))
    # Duke has a bye in date 16.
    cons.append(bye[15][DUKE])
    # Wake does not play home in date 17.
    cons.append(cz.Not(home[16][WAKE]))
    # Wake has a bye in the first date.
    cons.append(bye[0][WAKE])
    # Clemson, Duke, UMD and Wake do not play away in the last date.
    for i in [CLEM, DUKE, UMD, WAKE]:
        cons.append(cz.Not(away[days - 1][i]))
    # Clemson, FSU, GT and Wake do not play away in the first date.
    for i in [CLEM, FSU, GT, WAKE]:
        cons.append(cz.Not(away[0][i]))
    # Neither FSU nor NCSt has a bye in the last date.
    cons.append(cz.Not(bye[days - 1][FSU]))
    cons.append(cz.Not(bye[days - 1][NCST]))
    # UNC does not have a bye in the first date.
    cons.append(cz.Not(bye[0][UNC]))

    # Outputs: the opponent (or the team itself for a bye) and the venue code.
    for d in range(days):
        for i in range(n):
            cons.append(cz.Implies(bye[d][i], config[d][i] == i))
            cons.append(cz.Implies(bye[d][i], where[d][i] == 1))
            cons.append(cz.Implies(home[d][i], where[d][i] == 0))
            cons.append(cz.Implies(away[d][i], where[d][i] == 2))
            for j in range(n):
                if j != i:
                    cons.append(cz.Implies(play(d, i, j), config[d][i] == j))
            cons.append(config[d][i] >= 0)
            cons.append(config[d][i] < n)
            cons.append(where[d][i] >= 0)
            cons.append(where[d][i] <= 2)

    outputs = {
        "config": [[config[d][i] for i in range(n)] for d in range(days)],
        "where": [[where[d][i] for i in range(n)] for d in range(days)],
    }
    return cons, outputs
