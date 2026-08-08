import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# 1. Immutable input data (exactly as supplied)
# --------------------------------------------------
n_boats = 5                    # Number of boats
n_periods = 4                  # Number of successive half-hour periods
capacity = [6, 8, 12, 12, 12]  # On-board capacities for every boat
crew_size = [2, 2, 2, 2, 4]    # Crew sizes (people) for every boat

# Convenience index sets
BOATS   = range(n_boats)
PERIODS = range(n_periods)

# --------------------------------------------------
# 2. CP-SAT model
# --------------------------------------------------
model = cp_model.CpModel()

# 2.1 Decision variables
# ----------------------
# is_host[i] == 1  -> boat i is selected as a host
is_host = [model.NewBoolVar(f"host[{i}]") for i in BOATS]

# x[i][t][h] == 1 -> crew i is on host h during period t
x = [[[model.NewBoolVar(f"x[{i},{t},{h}]") for h in BOATS]
       for t in PERIODS]
       for i in BOATS]

# Auxiliary variables for pair-wise meetings
# y[i,j,t,h] == 1 -> crews i and j meet on host h in period t (i < j)
y = {}
for i in BOATS:
    for j in BOATS:
        if i < j:
            for t in PERIODS:
                for h in BOATS:
                    y[(i, j, t, h)] = model.NewBoolVar(f"y[{i},{j},{t},{h}]")

# --------------------------------------------------
# 3. Constraints
# --------------------------------------------------
# (1) Each crew must be somewhere every period
for i in BOATS:
    for t in PERIODS:
        model.Add(sum(x[i][t][h] for h in BOATS) == 1)

# (2) Only host boats can receive visitors
for i in BOATS:
    for t in PERIODS:
        for h in BOATS:
            model.Add(x[i][t][h] <= is_host[h])

# (3) Host crews stay on their own boat for all periods
for i in BOATS:
    for t in PERIODS:
        model.Add(x[i][t][i] == is_host[i])

# (4) No crew may visit the same host more than once (excluding its own boat)
for i in BOATS:
    for h in BOATS:
        if i != h:
            model.Add(sum(x[i][t][h] for t in PERIODS) <= 1)

# (5) At most one meeting between any pair of crews
for i in BOATS:
    for j in BOATS:
        if i < j:
            for t in PERIODS:
                for h in BOATS:
                    # Linking y and x variables
                    model.Add(y[(i, j, t, h)] <= x[i][t][h])
                    model.Add(y[(i, j, t, h)] <= x[j][t][h])
                    model.Add(y[(i, j, t, h)] >= x[i][t][h] + x[j][t][h] - 1)
            # At most one meeting in total
            model.Add(sum(y[(i, j, t, h)] for t in PERIODS for h in BOATS) <= 1)

# (6) Capacity of every host in every period must not be exceeded
for h in BOATS:
    for t in PERIODS:
        model.Add(sum(crew_size[i] * x[i][t][h] for i in BOATS) <= capacity[h])

# (7) At least one host boat must be designated
model.Add(sum(is_host) >= 1)

# --------------------------------------------------
# 4. Objective: minimise the number of host boats
# --------------------------------------------------
model.Minimize(sum(is_host))

# --------------------------------------------------
# 5. Solve
# --------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0  # safety limit
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise ValueError("No feasible solution found for the given data.")

# --------------------------------------------------
# 6. Extract solution
# --------------------------------------------------
solution_is_host = [int(solver.Value(is_host[i])) for i in BOATS]

# visits[i][t] = h – index of host boat occupied by crew i in period t
visits = [[None for _ in PERIODS] for _ in BOATS]
for i in BOATS:
    for t in PERIODS:
        for h in BOATS:
            if solver.Value(x[i][t][h]):
                visits[i][t] = h
                break

# --------------------------------------------------
# 7. Output as JSON
# --------------------------------------------------
print(json.dumps({
    "is_host": solution_is_host,
    "visits": visits
}))