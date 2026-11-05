#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob026_sport_scheduling.py
# Source description: https://www.csplib.org/Problems/prob026/

# Data
n_teams = 8  # Number of teams
# End of data

# Import libraries
import json
from cpmpy import *
from cpmpy.expressions.utils import all_pairs
import numpy as np


def sport_scheduling(n_teams):
    n_weeks, n_periods, n_matches = n_teams - 1, n_teams // 2, (n_teams - 1) * n_teams // 2

    home = intvar(1, n_teams, shape=(n_weeks, n_periods), name="home")
    away = intvar(1, n_teams, shape=(n_weeks, n_periods), name="away")

    model = Model()

    # teams cannot play each other
    model += home != away

    # every teams plays once a week
    # can be written cleaner, see issue #117
    # model += AllDifferent(np.append(home, away, axis=1), axis=0)
    for w in range(n_weeks):
        model += AllDifferent(np.append(home[w], away[w]))

    # every team plays each other
    for t1, t2 in all_pairs(range(1, n_teams + 1)):
        model += (sum((home == t1) & (away == t2)) + sum((home == t2) & (away == t1))) >= 1

    # every team plays at most twice in the same period
    for t in range(1, n_teams + 1):
        # can be written cleaner, see issue #117
        # sum((home == t) | (away == t), axis=1) <= 2
        for p in range(n_periods):
            model += sum((home[:, p] == t) | (away[:, p] == t)) <= 2

    return model, (home, away)


# Example usage
model, (home, away) = sport_scheduling(n_teams)
model.solve()

# Print
solution = {
    "home": home.value().tolist(),
    "away": away.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
