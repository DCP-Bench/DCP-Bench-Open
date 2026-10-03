"""Sports tournament scheduling (CSPLib 26): n teams play over n - 1 weeks, each week split
into n / 2 periods with one match per period. Every team plays once a week, every pair of
teams meets, and no team plays more than twice in the same period.

The model reports, for every week and period, the home team and the away team (1..n).
"""
import pulp


def build(instance):
    n = instance["n_teams"]
    n_weeks, n_periods = n - 1, n // 2
    teams = range(1, n + 1)
    weeks = range(n_weeks)
    periods = range(n_periods)
    # a match is an ordered pair (home, away) of different teams
    matches = [(i, j) for i in teams for j in teams if i != j]

    problem = pulp.LpProblem("sports_tournament_scheduling", pulp.LpMinimize)  # satisfaction

    # play[w][p][(i, j)] = 1 if in week w, period p, team i plays at home against team j
    play = [[{(i, j): pulp.LpVariable(f"play_{w}_{p}_{i}_{j}", cat="Binary") for i, j in matches}
             for p in periods] for w in weeks]

    # every slot holds one match, with two different teams
    for w in weeks:
        for p in periods:
            problem += pulp.lpSum(play[w][p].values()) == 1

    def involves(w, p, t):
        """1 if team t plays (home or away) in week w, period p"""
        return pulp.lpSum(var for (i, j), var in play[w][p].items() if t in (i, j))

    # every team plays once a week
    for w in weeks:
        for t in teams:
            problem += pulp.lpSum(involves(w, p, t) for p in periods) == 1

    # every team plays each other team (in either order)
    for i in teams:
        for j in teams:
            if i < j:
                problem += pulp.lpSum(play[w][p][(i, j)] + play[w][p][(j, i)]
                                      for w in weeks for p in periods) >= 1

    # every team plays at most twice in the same period
    for t in teams:
        for p in periods:
            problem += pulp.lpSum(involves(w, p, t) for w in weeks) <= 2

    home = [[pulp.lpSum(i * var for (i, j), var in play[w][p].items()) for p in periods]
            for w in weeks]
    away = [[pulp.lpSum(j * var for (i, j), var in play[w][p].items()) for p in periods]
            for w in weeks]
    return problem, {"home": home, "away": away}
