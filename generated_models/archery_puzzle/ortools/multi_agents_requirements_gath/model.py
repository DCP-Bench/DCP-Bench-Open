import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Immutable problem data
# --------------------------------------------------
SCORES = [16, 17, 23, 24, 39, 40]   # points per hit for each target
TARGET_TOTAL = 100                  # score we want to approximate
N_TARGETS = len(SCORES)

# --------------------------------------------------
# CP-SAT model
# --------------------------------------------------
model = cp_model.CpModel()

# Decision variables: number of hits on each target
# Upper bound 100 is more than sufficient (100 arrows of value 16 already score 1600)
HITS_UPPER = 100
hits = [model.NewIntVar(0, HITS_UPPER, f"hits_{i}") for i in range(N_TARGETS)]

# Auxiliary variable: total score obtained
max_total_possible = HITS_UPPER * max(SCORES) * N_TARGETS  # safe upper bound
total_score = model.NewIntVar(0, max_total_possible, "total_score")
model.Add(total_score == sum(SCORES[i] * hits[i] for i in range(N_TARGETS)))

# Auxiliary variable: absolute deviation from 100
deviation = model.NewIntVar(0, max_total_possible, "deviation")
model.Add(deviation >= total_score - TARGET_TOTAL)
model.Add(deviation >= TARGET_TOTAL - total_score)

# Objective: minimise deviation
model.Minimize(deviation)

# --------------------------------------------------
# Solve
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible solution found.")

solution_hits = [solver.Value(h) for h in hits]

# --------------------------------------------------
# Output
# --------------------------------------------------
print(json.dumps({"hits": solution_hits}))