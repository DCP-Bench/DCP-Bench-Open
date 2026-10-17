# Sports tournament scheduling (CSPLib 026).
# A tournament of n teams over n-1 weeks. Each week has n/2 periods, and each
# period holds one match: the first team plays home, the second plays away.
# home[w][p] and away[w][p] are the teams (numbered 1 to n) in week w, period p.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n_teams"]
    weeks = n - 1
    periods = n // 2
    home = [[cz.Int(f"home_{w}_{p}") for p in range(periods)] for w in range(weeks)]
    away = [[cz.Int(f"away_{w}_{p}") for p in range(periods)] for w in range(weeks)]

    constraints = []

    # Teams are numbered from 1 to n.
    for w in range(weeks):
        for p in range(periods):
            constraints += [home[w][p] >= 1, home[w][p] <= n,
                            away[w][p] >= 1, away[w][p] <= n]
            # A match pairs two different teams.
            constraints.append(home[w][p] != away[w][p])

    # Every team plays once a week: the n slots of a week (2 per period) hold
    # each team exactly once.
    for w in range(weeks):
        slots = [home[w][p] for p in range(periods)] + [away[w][p] for p in range(periods)]
        constraints.append(cz.Distinct(slots))

    # Every team plays at most twice in the same period over the tournament.
    for p in range(periods):
        for t in range(1, n + 1):
            hits = []
            for w in range(weeks):
                hits.append(cz.If(home[w][p] == t, 1, 0))
                hits.append(cz.If(away[w][p] == t, 1, 0))
            constraints.append(cz.Sum(hits) <= 2)

    # Every team plays every other team.
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            meetings = []
            for w in range(weeks):
                for p in range(periods):
                    meetings.append(cz.Or(
                        cz.And(home[w][p] == i, away[w][p] == j),
                        cz.And(home[w][p] == j, away[w][p] == i)))
            constraints.append(cz.Or(meetings))

    return constraints, {"home": home, "away": away}
