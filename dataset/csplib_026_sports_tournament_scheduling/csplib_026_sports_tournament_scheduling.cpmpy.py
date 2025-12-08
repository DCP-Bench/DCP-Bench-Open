#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob026_sport_scheduling.py
# Source description: https://www.csplib.org/Problems/prob026/

"""
The problem is to schedule a tournament of \( n \) teams over \( n-1 \) weeks, with each week divided into \( n/2 \)
periods, and each period divided into two slots. The first team in each slot plays at home, whilst the second plays
the first team away. A tournament must satisfy the following three constraints: every team plays once a week; every
team plays at most twice in the same period over the tournament; every team plays every other team.

An example schedule for 8 teams is:

| Week 1  | Week 2  | Week 3  | Week 4  | Week 5  | Week 6  | Week 7  |
|---------|---------|---------|---------|---------|---------|---------|
| 0 v 1   | 0 v 2   | 4 v 7   | 3 v 6   | 3 v 7   | 1 v 5   | 2 v 4   |
| 2 v 3   | 1 v 7   | 0 v 3   | 5 v 7   | 1 v 4   | 0 v 6   | 5 v 6   |
| 4 v 5   | 3 v 5   | 1 v 6   | 0 v 4   | 2 v 6   | 2 v 7   | 0 v 7   |
| 6 v 7   | 4 v 6   | 2 v 5   | 1 v 2   | 0 v 5   | 3 v 4   | 1 v 3   |

Print the home and away schedules (home, away) as lists of lists, where, e.g. home[w][p] is the team playing
home in week w and period p. The teams are numbered from 1 to n.
"""

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
