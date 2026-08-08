# Import libraries
from cpmpy import *
import json

# Parameters
n_teams = 8  # Number of teams
n_weeks = n_teams - 1  # Number of weeks
n_periods = n_teams // 2  # Number of periods per week

# Decision Variables
home = intvar(1, n_teams, shape=(n_weeks, n_periods), name="home")  # Home teams
away = intvar(1, n_teams, shape=(n_weeks, n_periods), name="away")  # Away teams

# Model
model = Model()

# Constraint: Every team plays once a week
for w in range(n_weeks):
    model += AllDifferent([home[w,p] for p in range(n_periods)] + [away[w,p] for p in range(n_periods)])

# Constraint: Every team plays at most twice in the same period over the tournament
for t in range(1, n_teams+1):
    for p in range(n_periods):
        model += sum((home[:,p] == t) | (away[:,p] == t)) <= 2

# Constraint: Every team plays every other team exactly once
for t1 in range(1, n_teams+1):
    for t2 in range(t1+1, n_teams+1):
        model += sum([(home[w,p] == t1) & (away[w,p] == t2) for w in range(n_weeks) for p in range(n_periods)]) + \
                 sum([(home[w,p] == t2) & (away[w,p] == t1) for w in range(n_weeks) for p in range(n_periods)]) == 1

# Constraint: No team plays against itself
for w in range(n_weeks):
    for p in range(n_periods):
        model += home[w,p] != away[w,p]

# Solve
model.solve()

# Print solution
solution = {
    "home": home.value().tolist(),
    "away": away.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script