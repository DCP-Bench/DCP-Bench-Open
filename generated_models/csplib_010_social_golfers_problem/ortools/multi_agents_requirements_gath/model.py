import json
from ortools.sat.python import cp_model

# -------------------------
# Input data (immutable)
# -------------------------

n_weeks = 4      # Number of weeks
n_groups = 3     # Number of groups formed each week
group_size = 3   # Golfers per group
n_golfers = n_groups * group_size  # Total number of golfers (derived – do not redefine)

# -------------------------
# Model creation
# -------------------------

model = cp_model.CpModel()

# Decision variables: assign[w][g][p] = 1 if golfer p is in group g on week w.
assign = [[[model.NewBoolVar(f"assign_w{w}_g{g}_p{p}")
            for p in range(n_golfers)]
           for g in range(n_groups)]
          for w in range(n_weeks)]

# -------------------------
# Constraints
# -------------------------

# C1. Weekly participation – every golfer plays exactly once per week.
for w in range(n_weeks):
    for p in range(n_golfers):
        model.Add(sum(assign[w][g][p] for g in range(n_groups)) == 1)

# C2. Group capacity – every group contains exactly group_size golfers each week.
for w in range(n_weeks):
    for g in range(n_groups):
        model.Add(sum(assign[w][g][p] for p in range(n_golfers)) == group_size)

# C3. Pair uniqueness – no two golfers play together more than once over all weeks.
for p in range(n_golfers):
    for q in range(p + 1, n_golfers):
        together_vars = []  # y_{w,g}(p,q)
        for w in range(n_weeks):
            for g in range(n_groups):
                y = model.NewBoolVar(f"pair_p{p}_q{q}_w{w}_g{g}")
                # y can only be 1 if both golfers are in this group
                model.Add(y <= assign[w][g][p])
                model.Add(y <= assign[w][g][q])
                # If both golfers are in the group, y must be 1
                model.Add(assign[w][g][p] + assign[w][g][q] - y <= 1)
                together_vars.append(y)
        # At most once over the whole horizon
        model.Add(sum(together_vars) <= 1)

# -------------------------
# Solve the model
# -------------------------

solver = cp_model.CpSolver()
# Optional: small time limit; instance is tiny, so default is fine
# solver.parameters.max_time_in_seconds = 10

status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible solution found for the given parameters.")

# -------------------------
# Extract solution
# -------------------------

solution_assign = [[[int(solver.Value(assign[w][g][p]))
                     for p in range(n_golfers)]
                    for g in range(n_groups)]
                   for w in range(n_weeks)]

# -------------------------
# Output (JSON)
# -------------------------

print(json.dumps({"assign": solution_assign}))
