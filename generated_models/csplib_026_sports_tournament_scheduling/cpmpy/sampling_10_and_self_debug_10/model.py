
import cpmpy as cp
import json
import numpy as np

# Data
n_teams = 8  # Number of teams
n_weeks = n_teams - 1
n_periods = n_teams // 2

# Model definition
model = cp.Model()

# Decision variables:
# home[w, p] = team playing at home in week w, period p
# away[w, p] = team playing away in week w, period p
home = cp.intvar(0, n_teams - 1, shape=(n_weeks, n_periods), name="home")
away = cp.intvar(0, n_teams - 1, shape=(n_weeks, n_periods), name="away")

# Constraints

# 1) Every team plays once a week (either home or away)
for w in range(n_weeks):
    # Collect all teams playing this week (home and away)
    teams_this_week = []
    for p in range(n_periods):
        teams_this_week.append(home[w, p])
        teams_this_week.append(away[w, p])
    # All teams playing this week are distinct
    model += cp.AllDifferent(teams_this_week)

# 2) Every team plays at most twice in the same period over the tournament
# For each team and each period, count how many times the team appears in that period (home or away)
for t in range(n_teams):
    for p in range(n_periods):
        # Count occurrences of team t in home[:, p] and away[:, p]
        count_home = cp.Count(home[:, p], t)
        count_away = cp.Count(away[:, p], t)
        model += (count_home + count_away) <= 2

# 3) Every team plays every other team exactly once
# The pairs (home[w,p], away[w,p]) represent matches
# We must ensure that each unordered pair of teams appears exactly once
# We create a matrix to count matches between teams
# Since matches are unordered pairs, we consider min and max of home and away to represent the pair uniquely

# Create a matrix to count matches between teams
# matches[i,j] = number of matches between team i and j (i<j)
matches = np.zeros((n_teams, n_teams), dtype=object)
for i in range(n_teams):
    for j in range(n_teams):
        if i < j:
            matches[i, j] = cp.intvar(0, 1, name=f"match_{i}_{j}")
        else:
            matches[i, j] = 0  # no variable needed for i>=j

# Link matches variables with schedule
# For each week and period, the pair (home, away) corresponds to one match
# For each match variable matches[i,j], it is 1 if the pair (i,j) appears in the schedule, else 0
for w in range(n_weeks):
    for p in range(n_periods):
        h = home[w, p]
        a = away[w, p]
        # We create boolean variables for each possible pair to indicate if this slot is that pair
        # But to avoid too many variables, we use element constraints and reification
        # Instead, we enforce that for the pair (min(h,a), max(h,a)), matches[min,max] == 1
        # We do this by summing over all slots and equating to matches[i,j]
        # So we accumulate counts for each pair over all slots

# We accumulate counts for each pair over all slots
# For each pair (i,j), sum over all slots of indicator that slot is (i,j) or (j,i) == matches[i,j]
for i in range(n_teams):
    for j in range(i + 1, n_teams):
        indicators = []
        for w in range(n_weeks):
            for p in range(n_periods):
                # Boolean variable indicating if slot (w,p) is match (i,j)
                b1 = cp.boolvar()
                b2 = cp.boolvar()
                model += (home[w, p] == i).implies(b1)
                model += (home[w, p] != i).implies(~b1)
                model += (away[w, p] == j).implies(b2)
                model += (away[w, p] != j).implies(~b2)
                b_ij = cp.boolvar()
                model += b_ij == (b1 & b2)

                # Similarly for (j,i)
                b3 = cp.boolvar()
                b4 = cp.boolvar()
                model += (home[w, p] == j).implies(b3)
                model += (home[w, p] != j).implies(~b3)
                model += (away[w, p] == i).implies(b4)
                model += (away[w, p] != i).implies(~b4)
                b_ji = cp.boolvar()
                model += b_ji == (b3 & b4)

                indicators.append(b_ij)
                indicators.append(b_ji)
        model += cp.sum(indicators) == matches[i, j]

# Each pair must appear exactly once
for i in range(n_teams):
    for j in range(i + 1, n_teams):
        model += matches[i, j] == 1

# Additional constraints:
# No team plays itself
for w in range(n_weeks):
    for p in range(n_periods):
        model += home[w, p] != away[w, p]

# Solve the model
if model.solve():
    # Extract schedules as lists of lists
    home_schedule = home.value().tolist()
    away_schedule = away.value().tolist()
    solution = {'home': home_schedule, 'away': away_schedule}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
