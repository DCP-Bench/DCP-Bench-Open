# Import libraries
from cpmpy import *
import json

# Parameters
n_teams = 8  # Number of teams
n_weeks = n_teams - 1  # Number of weeks
n_periods = n_teams // 2  # Number of periods per week

# Decision variables
# home[w][p]: the home team in period p of week w
home = intvar(0, n_teams - 1, shape=(n_weeks, n_periods), name="home")
# away[w][p]: the away team in period p of week w
away = intvar(0, n_teams - 1, shape=(n_weeks, n_periods), name="away")

# Model
model = Model()

# Constraint 1: Every team plays once a week
for t in range(n_teams):
    for w in range(n_weeks):
        # Count how many times team t is in home or away in week w
        model += [sum((home[w, :] == t) | (away[w, :] == t)) == 1]

# Constraint 2: Every team plays at most twice in the same period over the tournament
for t in range(n_teams):
    for p in range(n_periods):
        # Count how many times team t plays in period p across all weeks
        model += [sum((home[:, p] == t) | (away[:, p] == t)) <= 2]

# Constraint 3: Every team plays every other team
for t1 in range(n_teams):
    for t2 in range(n_teams):
        if t1 != t2:
            # Team t1 must play against team t2 at least once (either as home or away)
            model += [sum((home == t1) & (away == t2)) + sum((home == t2) & (away == t1)) >= 1]

# Constraint 4: No team plays against itself
for w in range(n_weeks):
    for p in range(n_periods):
        model += [home[w, p] != away[w, p]]

# Solve the model
model.solve()

# Print the solution
solution = {
    "home": home.value().tolist(),
    "away": away.value().tolist()
}
print(json.dumps(solution))