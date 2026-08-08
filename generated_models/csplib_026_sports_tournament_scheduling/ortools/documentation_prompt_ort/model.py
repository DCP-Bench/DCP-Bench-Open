from ortools.sat.python import cp_model
import json

# Input data
n_teams = 8  # Number of teams
n_weeks = n_teams - 1
n_periods = n_teams // 2

# Model definition
model = cp_model.CpModel()

# Decision Variables
# home[w][p] = team playing at home in week w, period p
home = []
# away[w][p] = team playing away in week w, period p
away = []

for w in range(n_weeks):
    home.append([model.NewIntVar(0, n_teams - 1, f'home_w{w}_p{p}') for p in range(n_periods)])
    away.append([model.NewIntVar(0, n_teams - 1, f'away_w{w}_p{p}') for p in range(n_periods)])

# Constraints

# 1) Every team plays once a week (either home or away)
for w in range(n_weeks):
    # Collect all teams playing in week w
    teams_in_week = []
    for p in range(n_periods):
        teams_in_week.append(home[w][p])
        teams_in_week.append(away[w][p])
    # All teams in week w must be all different (each team plays once)
    model.AddAllDifferent(teams_in_week)

# 2) Every team plays at most twice in the same period over the tournament
# For each team and each period, count how many times the team appears in that period (home or away)
for t in range(n_teams):
    for p in range(n_periods):
        appearances = []
        for w in range(n_weeks):
            # Boolean variables indicating if team t plays home or away in week w, period p
            is_home = model.NewBoolVar(f'is_home_t{t}_w{w}_p{p}')
            is_away = model.NewBoolVar(f'is_away_t{t}_w{w}_p{p}')
            model.Add(home[w][p] == t).OnlyEnforceIf(is_home)
            model.Add(home[w][p] != t).OnlyEnforceIf(is_home.Not())
            model.Add(away[w][p] == t).OnlyEnforceIf(is_away)
            model.Add(away[w][p] != t).OnlyEnforceIf(is_away.Not())
            appearances.append(is_home)
            appearances.append(is_away)
        model.Add(sum(appearances) <= 2)

# 3) Every team plays every other team exactly once (round robin)
# For each pair of teams (t1, t2), there must be exactly one match where t1 plays home and t2 away or vice versa
for t1 in range(n_teams):
    for t2 in range(t1 + 1, n_teams):
        matches = []
        for w in range(n_weeks):
            for p in range(n_periods):
                # Boolean variables for match t1 home vs t2 away
                t1_home_t2_away = model.NewBoolVar(f't1{t1}_home_t2{t2}_away_w{w}_p{p}')
                model.Add(home[w][p] == t1).OnlyEnforceIf(t1_home_t2_away)
                model.Add(home[w][p] != t1).OnlyEnforceIf(t1_home_t2_away.Not())
                model.Add(away[w][p] == t2).OnlyEnforceIf(t1_home_t2_away)
                model.Add(away[w][p] != t2).OnlyEnforceIf(t1_home_t2_away.Not())

                # Boolean variables for match t2 home vs t1 away
                t2_home_t1_away = model.NewBoolVar(f't2{t2}_home_t1{t1}_away_w{w}_p{p}')
                model.Add(home[w][p] == t2).OnlyEnforceIf(t2_home_t1_away)
                model.Add(home[w][p] != t2).OnlyEnforceIf(t2_home_t1_away.Not())
                model.Add(away[w][p] == t1).OnlyEnforceIf(t2_home_t1_away)
                model.Add(away[w][p] != t1).OnlyEnforceIf(t2_home_t1_away.Not())

                matches.append(t1_home_t2_away)
                matches.append(t2_home_t1_away)
        model.Add(sum(matches) == 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    home_schedule = []
    away_schedule = []
    for w in range(n_weeks):
        home_week = []
        away_week = []
        for p in range(n_periods):
            home_week.append(solver.Value(home[w][p]))
            away_week.append(solver.Value(away[w][p]))
        home_schedule.append(home_week)
        away_schedule.append(away_week)
    solution = {
        'home': home_schedule,
        'away': away_schedule
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")