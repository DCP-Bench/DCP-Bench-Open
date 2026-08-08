import json
from ortools.sat.python import cp_model

# --------------------------
# Fixed input data (immutable)
# --------------------------
n_teams = 8  # Number of teams (must be even)

# --------------------------
# Derived dimensions
# --------------------------
weeks = n_teams - 1           # number of weeks
periods = n_teams // 2        # periods per week
max_per_period = 2            # Each team may appear in a period at most twice

T = range(n_teams)
W = range(weeks)
P = range(periods)

# --------------------------
# Model
# --------------------------
model = cp_model.CpModel()

# Integer variables giving the actual team numbers that play home/away in every slot
home = [[model.NewIntVar(0, n_teams - 1, f"home_w{w}_p{p}") for p in P] for w in W]
away = [[model.NewIntVar(0, n_teams - 1, f"away_w{w}_p{p}") for p in P] for w in W]

# Each slot must pair two distinct teams
for w in W:
    for p in P:
        model.Add(home[w][p] != away[w][p])

# -----------------------------------------------------------------
# Helper Boolean variables: does team t appear as home/away in slot?
# -----------------------------------------------------------------
home_is = [[[model.NewBoolVar(f"is_home_w{w}_p{p}_t{t}") for t in T] for p in P] for w in W]
away_is = [[[model.NewBoolVar(f"is_away_w{w}_p{p}_t{t}") for t in T] for p in P] for w in W]

for w in W:
    for p in P:
        # Link the Boolean indicators to the integer team numbers
        for t in T:
            model.Add(home[w][p] == t).OnlyEnforceIf(home_is[w][p][t])
            model.Add(home[w][p] != t).OnlyEnforceIf(home_is[w][p][t].Not())

            model.Add(away[w][p] == t).OnlyEnforceIf(away_is[w][p][t])
            model.Add(away[w][p] != t).OnlyEnforceIf(away_is[w][p][t].Not())

        # Exactly one team is the home side / away side in every slot
        model.AddExactlyOne(home_is[w][p])
        model.AddExactlyOne(away_is[w][p])

# ----------------------------------------------------------
# Constraint 1 – Each team plays exactly once per week
# ----------------------------------------------------------
for w in W:
    for t in T:
        appearances = [home_is[w][p][t] for p in P] + [away_is[w][p][t] for p in P]
        model.Add(sum(appearances) == 1)

# ----------------------------------------------------------
# Constraint 2 – A team uses a given period at most twice
# ----------------------------------------------------------
for p in P:
    for t in T:
        period_occ = [home_is[w][p][t] for w in W] + [away_is[w][p][t] for w in W]
        model.Add(sum(period_occ) <= max_per_period)

# -------------------------------------------------------------------------
# Helper Boolean variables: match_is[w][p][i][j] is true ⇔ home=i & away=j
# -------------------------------------------------------------------------
match_is = {}
for w in W:
    for p in P:
        slot_vars = []
        for i in T:
            for j in T:
                if i == j:
                    continue  # cannot play itself (already enforced)
                v = model.NewBoolVar(f"match_w{w}_p{p}_h{i}_a{j}")
                match_is[(w, p, i, j)] = v

                # If this ordered pair is selected ⇒ correct home/away indicators are true
                model.AddImplication(v, home_is[w][p][i])
                model.AddImplication(v, away_is[w][p][j])

                slot_vars.append(v)
        # Exactly one ordered pair is chosen in every slot
        model.AddExactlyOne(slot_vars)

# ----------------------------------------------------------
# Constraint 3 – Every unordered pair meets exactly once overall
# ----------------------------------------------------------
for i in T:
    for j in T:
        if i >= j:
            continue
        pair_occurrences = []
        for w in W:
            for p in P:
                pair_occurrences.append(match_is[(w, p, i, j)])  # i home, j away
                pair_occurrences.append(match_is[(w, p, j, i)])  # j home, i away
        model.Add(sum(pair_occurrences) == 1)

# ----------------------------------------------------------
# No optimisation objective – just find any feasible schedule
# ----------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safety limit (problem is tiny)
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible schedule found.")

# --------------------------
# Extract and print solution
# --------------------------
out_home = [[solver.Value(home[w][p]) for p in P] for w in W]
out_away = [[solver.Value(away[w][p]) for p in P] for w in W]

print(json.dumps({"home": out_home, "away": out_away}))