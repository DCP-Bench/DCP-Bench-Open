# Sports tournament scheduling (CSPLib 026).
# A tournament of n teams over n-1 weeks. Each week has n/2 periods, and each
# period holds one match: the first team plays home, the second plays away.
# home[w][p] and away[w][p] are the teams (numbered 1 to n) in week w, period p.
#
# Encoding: a Boolean play[w][p][i][j] says that in week w, period p, team i
# plays at home against team j. The Booleans are the decision; the outputs are
# read off them. Counting constraints are written as pairwise clauses over
# Booleans, which keeps the problem propositional.
import itertools

import cvc5.pythonic as cz


def build(instance):
    n = instance["n_teams"]
    weeks = n - 1
    periods = n // 2
    teams = range(1, n + 1)

    play = {}
    for w in range(weeks):
        for p in range(periods):
            for i in teams:
                for j in teams:
                    if i != j:
                        play[w, p, i, j] = cz.Bool(f"play_{w}_{p}_{i}_{j}")

    # inslot[w][p][t]: team t takes part in the match of week w, period p.
    inslot = {}
    for w in range(weeks):
        for p in range(periods):
            for t in teams:
                inslot[w, p, t] = cz.Bool(f"in_{w}_{p}_{t}")

    constraints = []

    # Every period holds exactly one match.
    for w in range(weeks):
        for p in range(periods):
            cells = [play[w, p, i, j] for i in teams for j in teams if i != j]
            constraints.append(cz.Or(cells))
            for a, b in itertools.combinations(cells, 2):
                constraints.append(cz.Not(cz.And(a, b)))

    # A team takes part in a period exactly when it is one of the two teams of its match.
    for w in range(weeks):
        for p in range(periods):
            for t in teams:
                opp = [play[w, p, t, j] for j in teams if j != t] + \
                      [play[w, p, j, t] for j in teams if j != t]
                constraints.append(inslot[w, p, t] == cz.Or(opp))

    # Every team plays once a week: exactly one of the periods of the week.
    for w in range(weeks):
        for t in teams:
            slots = [inslot[w, p, t] for p in range(periods)]
            constraints.append(cz.Or(slots))
            for a, b in itertools.combinations(slots, 2):
                constraints.append(cz.Not(cz.And(a, b)))

    # Every team plays at most twice in the same period over the tournament:
    # no three weeks in which it is in the same period.
    for p in range(periods):
        for t in teams:
            for ws in itertools.combinations(range(weeks), 3):
                constraints.append(cz.Not(cz.And([inslot[w, p, t] for w in ws])))

    # Every team plays every other team: each pair meets in some week and period.
    for i, j in itertools.combinations(teams, 2):
        meets = [cz.Or(play[w, p, i, j], play[w, p, j, i])
                 for w in range(weeks) for p in range(periods)]
        constraints.append(cz.Or(meets))
        for a, b in itertools.combinations(meets, 2):
            constraints.append(cz.Not(cz.And(a, b)))

    # Outputs: the home and away team of each week and period.
    home = [[cz.Int(f"home_{w}_{p}") for p in range(periods)] for w in range(weeks)]
    away = [[cz.Int(f"away_{w}_{p}") for p in range(periods)] for w in range(weeks)]
    for w in range(weeks):
        for p in range(periods):
            constraints.append(home[w][p] == cz.Sum(
                [cz.If(play[w, p, i, j], i, 0) for i in teams for j in teams if i != j]))
            constraints.append(away[w][p] == cz.Sum(
                [cz.If(play[w, p, i, j], j, 0) for i in teams for j in teams if i != j]))

    return constraints, {"home": home, "away": away}
