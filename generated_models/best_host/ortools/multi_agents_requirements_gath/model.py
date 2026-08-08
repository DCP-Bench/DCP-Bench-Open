import json
from ortools.sat.python import cp_model

# --------------------- Data ---------------------
# Guest codes (alphabetical order)
# 0 = Andrew, 1 = Betty, 2 = Cara, 3 = Dave, 4 = Erica, 5 = Frank
n_guests = 6

# Compatibility sets (symmetric)
compat = {
    0: {3, 5},  # Andrew  ↔ Dave, Frank
    1: {2, 4},  # Betty   ↔ Cara, Erica
    2: {1, 5},  # Cara    ↔ Betty, Frank
    3: {0, 4},  # Dave    ↔ Andrew, Erica
    4: {1, 3},  # Erica   ↔ Betty, Dave
    5: {0, 2},  # Frank   ↔ Andrew, Cara
}

# All ordered compatible pairs for quick lookup
good_pair = {(g, h) for g, neigh in compat.items() for h in neigh}

# Seat adjacency on a round table with 6 places
adjacent_edges = [(s, (s + 1) % n_guests) for s in range(n_guests)]

# --------------------- Model ---------------------
model = cp_model.CpModel()

# x[s] = guest sitting on seat s (0..5)
x = [model.NewIntVar(0, n_guests - 1, f"x[{s}]") for s in range(n_guests)]

# Each guest sits exactly once
model.AddAllDifferent(x)

# Break rotational symmetry: fix Andrew to seat 0
model.Add(x[0] == 0)

# Pre-build the compatibility table once
allowed_table = []
for a in range(n_guests):
    for b in range(n_guests):
        allowed_table.append([a, b, 1 if (a, b) in good_pair else 0])

# Boolean variable per edge indicating if the neighbouring guests are compatible
is_good = []
for s_left, s_right in adjacent_edges:
    g = model.NewBoolVar(f"good_{s_left}_{s_right}")
    is_good.append(g)
    model.AddAllowedAssignments([x[s_left], x[s_right], g], allowed_table)

# Objective: maximise number of compatible adjacencies (=> minimise conflicts)
model.Maximize(sum(is_good))

# --------------------- Solve ---------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    seating_order = [int(solver.Value(v)) for v in x]
    print(json.dumps({"x": seating_order}))
else:
    # The model is guaranteed to be feasible, but guard just in case
    raise RuntimeError("No feasible seating arrangement found.")
