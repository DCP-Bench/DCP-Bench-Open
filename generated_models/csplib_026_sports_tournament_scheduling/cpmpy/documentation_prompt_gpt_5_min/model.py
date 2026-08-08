
import cpmpy as cp
import json

# Data
n_teams = 8  # Number of teams
# End of data

n = n_teams
weeks = n - 1
periods = n // 2

# Model definition
model = cp.Model()

# Decision Variables
# home[w,p] is the home team in week w and period p
# away[w,p] is the away team in week w and period p
home = cp.intvar(1, n, shape=(weeks, periods), name="home")
away = cp.intvar(1, n, shape=(weeks, periods), name="away")

# Constraints
# 1) In each week, the 2*(n/2)=n slots are filled by all teams exactly once
for w in range(weeks):
    home_week = [home[w, p] for p in range(periods)]
    away_week = [away[w, p] for p in range(periods)]
    # all slots in a week must be different -> permutation of 1..n
    model += cp.AllDifferent(*(home_week + away_week))

# 2) In each period of a week, the home and away teams are different
for w in range(weeks):
    for p in range(periods):
        model += home[w, p] != away[w, p]

# 3) Every pair of teams meet exactly once (regardless of home/away)
for t1 in range(1, n + 1):
    for t2 in range(t1 + 1, n + 1):
        meetings = []
        for w in range(weeks):
            for p in range(periods):
                meetings.append((home[w, p] == t1) & (away[w, p] == t2))
                meetings.append((home[w, p] == t2) & (away[w, p] == t1))
        model += cp.sum(meetings) == 1

# 4) Every team plays at most twice in the same period over the tournament
for team in range(1, n + 1):
    for p in range(periods):
        plays_in_period = []
        for w in range(weeks):
            plays_in_period.append((home[w, p] == team) | (away[w, p] == team))
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
