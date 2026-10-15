# Sports tournament scheduling: n teams play a round robin over n-1 weeks.
# Each week has n/2 periods, and each period holds one game between a home
# team and an away team. Every team plays once a week, at most twice in the
# same period, and every pair of teams plays exactly once.
#
# Encoding: one-hot per (week, period) for the home team H[w][p][t] and the
# away team A[w][p][t]. The auxiliary M[w][p][i][j] says teams i and j play
# each other in period p of week w, in either order.

from paramita.modelling import Bool, Iff, Or


def build(instance):
    n = instance["n_teams"]
    weeks = n - 1
    periods = n // 2
    teams = range(n)

    H = [[[Bool(f"home_{w}_{p}_{t}") for t in teams] for p in range(periods)] for w in range(weeks)]
    A = [[[Bool(f"away_{w}_{p}_{t}") for t in teams] for p in range(periods)] for w in range(weeks)]

    cons = []

    # each slot holds exactly one team: one home team and one away team per game
    for w in range(weeks):
        for p in range(periods):
            cons.append(sum(H[w][p]) == 1)
            cons.append(sum(A[w][p]) == 1)

    # every team plays once a week (so it is home or away in exactly one period)
    for w in range(weeks):
        for t in teams:
            cons.append(sum(H[w][p][t] + A[w][p][t] for p in range(periods)) == 1)

    # every team plays at most twice in the same period over the tournament
    for p in range(periods):
        for t in teams:
            cons.append(sum(H[w][p][t] + A[w][p][t] for w in range(weeks)) <= 2)

    # every team plays every other team: each pair meets in exactly one game
    M = {}
    for w in range(weeks):
        for p in range(periods):
            for i in teams:
                for j in teams:
                    if i < j:
                        m = Bool(f"meet_{w}_{p}_{i}_{j}")
                        M[w, p, i, j] = m
                        cons.append(Iff(m, Or([H[w][p][i] & A[w][p][j], H[w][p][j] & A[w][p][i]])))
    for i in teams:
        for j in teams:
            if i < j:
                cons.append(sum(M[w, p, i, j] for w in range(weeks) for p in range(periods)) == 1)

    # output the schedule with teams numbered 1..n
    home = [[sum((t + 1) * H[w][p][t] for t in teams) for p in range(periods)] for w in range(weeks)]
    away = [[sum((t + 1) * A[w][p][t] for t in teams) for p in range(periods)] for w in range(weeks)]

    return cons, {"home": home, "away": away}
