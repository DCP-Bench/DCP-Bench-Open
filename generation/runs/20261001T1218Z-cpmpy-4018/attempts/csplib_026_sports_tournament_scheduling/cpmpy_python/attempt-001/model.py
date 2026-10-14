# Sports tournament scheduling: n teams (n even) play over n - 1 weeks, with n / 2 matches
# (periods) per week. In each match the first team plays at home and the second away. Every
# team plays once a week, at most twice in the same period over the tournament, and every
# team meets every other team.
import numpy as np
import cpmpy as cp


def build(instance):
    n_teams = instance["n_teams"]
    n_weeks = n_teams - 1
    n_periods = n_teams // 2

    # home[w, p] / away[w, p] = the home / away team (numbered from 1) of the match in
    # week w, period p
    home = cp.intvar(1, n_teams, shape=(n_weeks, n_periods), name="home")
    away = cp.intvar(1, n_teams, shape=(n_weeks, n_periods), name="away")

    model = cp.Model()

    # A team does not play against itself.
    model += home != away

    # Every team plays exactly once a week: the 2 * n_periods = n_teams places of a week hold
    # n_teams different teams.
    for w in range(n_weeks):
        model += cp.AllDifferent(np.append(home[w], away[w]))

    # Every team meets every other team, as home or away, in at least one match.
    for t1 in range(1, n_teams + 1):
        for t2 in range(t1 + 1, n_teams + 1):
            model += (cp.sum((home == t1) & (away == t2)) + cp.sum((home == t2) & (away == t1))) >= 1

    # Every team plays at most twice in the same period over the tournament.
    for t in range(1, n_teams + 1):
        for p in range(n_periods):
            model += cp.sum((home[:, p] == t) | (away[:, p] == t)) <= 2

    return model, {"home": home, "away": away}
