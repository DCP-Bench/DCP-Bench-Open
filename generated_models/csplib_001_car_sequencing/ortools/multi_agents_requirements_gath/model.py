# -------------------------------------------------------------
#  Feasible car-sequencing with station capacity constraints
#  Google OR-Tools CP-SAT implementation
# -------------------------------------------------------------

import json
from ortools.sat.python import cp_model

# ---------------------- 1. Input data ------------------------
at_most   = [1, 2, 2, 2, 1]  # maximum number of cars with the option inside any window
per_slots = [2, 3, 3, 5, 5]  # window size for each option

demand    = [1, 1, 2, 2, 2, 2]  # number of cars of each type that must be produced
requires  = [
    [1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0],
]  # requires[type][option] == 1 if car type needs option

# Derived constants
T = len(demand)          # number of car types
F = len(at_most)         # number of options / stations
N = sum(demand)          # length of the final sequence

# ------------------ 2. Build CP-SAT model --------------------
model = cp_model.CpModel()

# 2.1 Position-type assignment binary variables
#     x[j][t] == 1  ⇔  car type t is placed at position j
x = []
for j in range(N):
    x.append([model.NewBoolVar(f"x_{j}_{t}") for t in range(T)])

# 2.2 Exactly one car type per position
for j in range(N):
    model.Add(sum(x[j][t] for t in range(T)) == 1)

# 2.3 Satisfy demand for each car type
for t in range(T):
    model.Add(sum(x[j][t] for j in range(N)) == demand[t])

# 2.4 Station capacity – sliding-window limits
for o in range(F):
    window = per_slots[o]
    limit  = at_most[o]
    for start in range(N - window + 1):
        # Sum of cars requiring option o inside the window ≤ limit
        window_cars = []
        for j in range(start, start + window):
            for t in range(T):
                if requires[t][o]:
                    window_cars.append(x[j][t])
        if window_cars:  # Only add the constraint if someone actually can contribute
            model.Add(sum(window_cars) <= limit)
        else:
            # No type ever needs this option ⇒ constraint always satisfied
            pass

# 2.5 No objective – pure feasibility

# ---------------------- 3. Solve -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10.0  # small time limit just in case
status = solver.Solve(model)

# --------------------- 4. Output -----------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    sequence = []
    for j in range(N):
        for t in range(T):
            if solver.Value(x[j][t]):
                sequence.append(t)
                break

    print(json.dumps({"sequence": sequence}))
else:
    # If no solution is found we still have to print something to satisfy
    # the required output format. Here we return an empty list.
    print(json.dumps({"sequence": []}))
