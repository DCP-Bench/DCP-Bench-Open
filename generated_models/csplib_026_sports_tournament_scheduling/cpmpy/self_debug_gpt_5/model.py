
import cpmpy as cp
import json
import numpy as np

# Data (optional)
n_teams = 8  # Number of teams
# End of data

# Basic validation
if n_teams % 2 != 0 or n_teams < 2:
    print("No solution found.")
else:
    n = n_teams
    nweeks = n - 1
    nperiods = n // 2

    # Model definition
    model = cp.Model()

    # Decision Variables
    # home[w][p] is the team playing at home in week w and period p
    # away[w][p] is the team playing away in week w and period p
    home = cp.intvar(1, n, shape=(nweeks, nperiods), name="home")
    away = cp.intvar(1, n, shape=(nweeks, nperiods), name="away")

    # Constraints

    # 1) Every team plays exactly once per week (permutation of teams across all matches in the week)
    for w in range(nweeks):
        week_vars = list(home[w]) + list(away[w])
        model += cp.AllDifferent(week_vars)

    # 2) Each match has two different teams and break home/away symmetry by fixing order
    for w in range(nweeks):
        for p in range(nperiods):
            model += (home[w, p] < away[w, p])

    # 3) Every pair of teams plays exactly once over the tournament (undirected pairing)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pair_occurs = []
            for w in range(nweeks):
                for p in range(nperiods):
                    pair_occurs.append((home[w, p] == i) & (away[w, p] == j))
                    pair_occurs.append((home[w, p] == j) & (away[w, p] == i))
            model += (cp.sum(pair_occurs) == 1)

    # 4) Every team plays at most twice in the same period over the tournament
    for t in range(1, n + 1):
        for p in range(nperiods):
            plays_in_period = []
            for w in range(nweeks):
                plays_in_period.append(home[w, p] == t)
                plays_in_period.append(away[w, p] == t)
            model += (cp.sum(plays_in_period) <= 2)

    # Symmetry breaking: fix the first week's pairings
    # This also helps the solver converge faster
    # Week 0: (1 v 2), (3 v 4), (5 v 6), (7 v 8)
    model += [
        home[0, 0] == 1, away[0, 0] == 2,
        home[0, 1] == 3, away[0, 1] == 4,
        home[0, 2] == 5, away[0, 2] == 6,
        home[0, 3] == 7, away[0, 3] == 8
    ]

    # Solve and print
    if model.solve():
        solution = {
            'home': home.value().tolist(),
            'away': away.value().tolist()
        }
        print(json.dumps(solution, indent=4))
    else:
        print("No solution found.")
