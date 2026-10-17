# Sports tournament scheduling (CSPLib 026).
# A tournament of n teams over n-1 weeks. Each week has n/2 periods, and each
# period holds one match: the first team plays home, the second plays away.
# home[w][p] and away[w][p] are the teams (numbered 1 to n) in week w, period p.
#
# Encoding: a Boolean play[w][p][i][j] says that in week w, period p, team i
# plays at home against team j. Each period holds exactly one match, so the
# outputs are read off these Booleans.
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

    def plays_in(w, p, t):
        # Team t takes part in the match of week w, period p.
        return cz.Or([play[w, p, t, j] for j in teams if j != t] +
                     [play[w, p, j, t] for j in teams if j != t])

    constraints = []

    # Every period holds exactly one match.
    for w in range(weeks):
        for p in range(periods):
            cells = list(play.items())
            cells = [(k, v) for k, v in cells if k[0] == w and k[1] == p]
            constraints.append(cz.Or([v for _, v in cells]))
            for a in range(len(cells)):
                for b in range(a + 1, len(cells)):
                    constraints.append(cz.Not(cz.And(cells[a][1], cells[b][1])))

    # Every team plays once a week: it is in exactly one of the periods of each week.
    for w in range(weeks):
        for t in teams:
            constraints.append(cz.Sum([cz.If(plays_in(w, p, t), 1, 0)
                                       for p in range(periods)]) == 1)

    # Every team plays at most twice in the same period over the tournament.
    for p in range(periods):
        for t in teams:
            constraints.append(cz.Sum([cz.If(plays_in(w, p, t), 1, 0)
                                       for w in range(weeks)]) <= 2)

    # Every team plays every other team.
    for i in teams:
        for j in teams:
            if i < j:
                constraints.append(cz.Or([cz.Or(play[w, p, i, j], play[w, p, j, i])
                                          for w in range(weeks)
                                          for p in range(periods)]))

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
