
import cpmpy as cp
import json

# Data
n_teams = 8  # Number of teams
# End of data

# Derived sizes
weeks = n_teams - 1
periods = n_teams // 2

# Model definition
model = cp.Model()

# Decision Variables
# home[w][p] is the team playing at home in week w, period p (1..n_teams)
# away[w][p] is the team playing away in week w, period p (1..n_teams)
home = cp.intvar(1, n_teams, shape=(weeks, periods), name="home")
away = cp.intvar(1, n_teams, shape=(weeks, periods), name="away")

# Constraints

# 1) In each slot, home and away are different
for w in range(weeks):
    for p in range(periods):
        model += (home[w, p] != away[w, p])

# 2) Every team plays exactly once each week:
#    For each week, the set of home teams and away teams (combined) are all different
for w in range(weeks):
    positions = [home[w, p] for p in range(periods)] + [away[w, p] for p in range(periods)]
    model += cp.AllDifferent(*positions)

# 3) Every team plays every other team exactly once (unordered)
for t1 in range(1, n_teams + 1):
    for t2 in range(t1 + 1, n_teams + 1):
        occ = []
        for w in range(weeks):
            for p in range(periods):
                occ.append((home[w, p] == t1) & (away[w, p] == t2))
                occ.append((home[w, p] == t2) & (away[w, p] == t1))
        model += cp.sum(occ) == 1

# 4) Every team plays at most twice in the same period over the tournament
for t in range(1, n_teams + 1):
    for p in range(periods):
        plays_in_period = []
        for w in range(weeks):
            plays_in_period.append((home[w, p] == t) | (away[w, p] == t))
        model += cp.sum(plays_in_period) <= 2

# Solve and print
if model.solve():
    solution = {
        'home': home.value().tolist(),
        'away': away.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
