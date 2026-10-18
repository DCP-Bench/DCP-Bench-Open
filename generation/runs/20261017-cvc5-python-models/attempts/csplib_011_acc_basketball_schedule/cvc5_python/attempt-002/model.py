# csplib_011 ACC basketball schedule (1997/98): a double round-robin of 9 teams over 18 dates,
# with mirroring, home/away/bye pattern, weekend pattern, first-weekend, rival, constrained
# match, opponent sequence and other constraints from the description.
# Encoding: Boolean home[d][t][u] (t hosts u on date d) and bye[d][t]; all counts are
# Sum(If(...)) under QF_LIA. Team order and date numbering follow the description (dates 1..n).
import itertools

from cvc5.pythonic import And, Bool, If, Not, Or, Sum, SolverFor

CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}
MIRROR = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]


def build(instance):
    n_days = instance["n_days"]
    n_teams = instance["n_teams"]
    days = range(1, n_days + 1)
    teams = range(n_teams)

    home_var = {
        d: {t: {u: Bool(f"h_{d}_{t}_{u}") for u in teams if u != t} for t in teams}
        for d in days
    }
    bye = {d: {t: Bool(f"b_{d}_{t}") for t in teams} for d in days}

    def home(d, t):
        return Or([home_var[d][t][u] for u in teams if u != t])

    def away(d, t):
        return Or([home_var[d][u][t] for u in teams if u != t])

    def plays(d, t, u):
        return Or(home_var[d][t][u], home_var[d][u][t])

    def commitments(d, t):
        # every literal that says team t has a game or a bye on date d
        return [bye[d][t]] + [home_var[d][t][u] for u in teams if u != t] \
            + [home_var[d][u][t] for u in teams if u != t]

    def exactly_one(lits, cons):
        cons.append(Or(lits))
        for i in range(len(lits)):
            for j in range(i + 1, len(lits)):
                cons.append(Or(Not(lits[i]), Not(lits[j])))

    cons = []

    # Double round robin: each team plays each other once at home and once away.
    for u in teams:
        for t in teams:
            if u != t:
                exactly_one([home_var[d][t][u] for d in days], cons)

    # Each team plays one game or has a bye on each date.
    for d in days:
        for t in teams:
            exactly_one(commitments(d, t), cons)

    # Derived totals: 18 dates and 16 games per team give 2 byes per team; 9 teams give
    # one bye per date and 4 games per date.
    for t in teams:
        cons.append(Sum([If(bye[d][t], 1, 0) for d in days]) == 2)
    for d in days:
        cons.append(Sum([If(bye[d][t], 1, 0) for t in teams]) == 1)
        cons.append(Sum([If(home_var[d][t][u], 1, 0) for t in teams for u in teams if u != t]) == 4)

    # Mirroring: dates r1 and r2 pair up, each team meets the same opponent on both dates,
    # with home and away swapped, and a bye stays a bye.
    for r1, r2 in MIRROR:
        for t in teams:
            cons.append(bye[r1][t] == bye[r2][t])
            for u in teams:
                if u != t:
                    cons.append(home_var[r1][t][u] == home_var[r2][u][t])

    # Weekend pattern: on the weekends (even dates) each team plays four home, four away and
    # one bye.
    weekends = [d for d in days if d % 2 == 0]
    for t in teams:
        cons.append(Sum([If(home(d, t), 1, 0) for d in weekends]) == 4)
        cons.append(Sum([If(away(d, t), 1, 0) for d in weekends]) == 4)
        cons.append(Sum([If(bye[d][t], 1, 0) for d in weekends]) == 1)

    # First weekends: home matches or byes on at least two of the first five weekends.
    for t in teams:
        cons.append(Sum([If(Or(home(d, t), bye[d][t]), 1, 0) for d in (2, 4, 6, 8, 10)]) >= 2)

    # Home/away/bye pattern: at most two away in a row, at most two home in a row, at most
    # three away or byes in a row, at most four home or byes in a row.
    for t in teams:
        for d in range(1, n_days - 1):
            cons.append(Not(And([away(x, t) for x in range(d, d + 3)])))
            cons.append(Not(And([home(x, t) for x in range(d, d + 3)])))
        for d in range(1, n_days - 2):
            cons.append(Not(And([Or(away(x, t), bye[x][t]) for x in range(d, d + 4)])))
        for d in range(1, n_days - 3):
            cons.append(Not(And([Or(home(x, t), bye[x][t]) for x in range(d, d + 5)])))

    # No two final aways: no team plays away on both last dates.
    last = n_days
    for t in teams:
        cons.append(Not(And(away(last - 1, t), away(last, t))))

    # Rival matches: on the last date every team except FSU plays its rival, unless it plays
    # FSU or has a bye.
    for t, rival in RIVAL.items():
        cons.append(Or(plays(last, t, rival), plays(last, t, FSU), bye[last][t]))

    # Constrained matches: these pairings occur at least once in dates 11 to 18.
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        cons.append(Or([plays(d, a, b) for d in range(11, 19)]))

    # Opponent sequence: no team plays away against UNC and Duke on consecutive dates.
    for d in range(1, n_days):
        for t in teams:
            for x, y in [(UNC, DUKE), (DUKE, UNC)]:
                if t not in (x, y):
                    cons.append(Not(And(home_var[d][x][t], home_var[d + 1][y][t])))
    # No team plays against UNC, Duke and Wake on three consecutive dates (any order).
    trio = [UNC, DUKE, WAKE]
    for d in range(1, n_days - 1):
        for t in teams:
            if t in trio:
                continue
            for a, b, c in itertools.permutations(trio):
                cons.append(Not(And(plays(d, t, a), plays(d + 1, t, b), plays(d + 2, t, c))))

    # Other constraints from the description.
    cons.append(plays(last, UNC, DUKE))           # UNC plays Duke on the last date
    cons.append(plays(11, UNC, DUKE))             # and on date 11
    cons.append(plays(2, UNC, CLEM))              # UNC plays Clem in the second date
    cons.append(bye[16][DUKE])                    # Duke has a bye in date 16
    cons.append(Not(home(17, WAKE)))              # Wake does not play home in date 17
    cons.append(bye[1][WAKE])                     # Wake has a bye in the first date
    for t in (CLEM, DUKE, UMD, WAKE):             # no away game in the last date
        cons.append(Not(away(last, t)))
    for t in (CLEM, FSU, GT, WAKE):               # no away game in the first date
        cons.append(Not(away(1, t)))
    cons.append(Not(bye[last][FSU]))              # FSU and NCSt have no bye in the last date
    cons.append(Not(bye[last][NCST]))
    cons.append(Not(bye[1][UNC]))                 # UNC has no bye in the first date

    # Outputs: config[d][i] is the opponent of team i on date d (i itself on a bye);
    # where[d][i] is 0 at home, 1 on a bye, 2 away.
    config = [
        [Sum([If(bye[d][i], i, 0)] + [If(plays(d, i, j), j, 0) for j in teams if j != i])
         for i in teams]
        for d in days
    ]
    where = [
        [If(home(d, i), 0, If(bye[d][i], 1, 2)) for i in teams]
        for d in days
    ]

    solver = SolverFor("QF_LIA")
    solver.add(*cons)
    return solver, {"config": config, "where": where}
