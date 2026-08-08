import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# 1. Input parsing (exactly as provided – here the block is empty)
# ---------------------------------------------------------------------------
# The problem instance is fully defined by the statement; no external data to
# read. Nevertheless, we keep the section for completeness and future-proofing.

# ---------------------------------------------------------------------------
# 2. Model creation
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Constants
NUM_BOWLS = 40    # total bowls, numbered 1..40
NUM_ORANGES = 9   # oranges to place

# ---------------------------------------------------------------------------
# 3. Decision variables
#    x[k] – position (bowl index) of the k-th orange (k = 0..8)
# ---------------------------------------------------------------------------
x = [model.NewIntVar(1, NUM_BOWLS, f"x[{k}]") for k in range(NUM_ORANGES)]

# Optional: enforce increasing order to cut symmetry and speed up search.
for k in range(NUM_ORANGES - 1):
    model.Add(x[k] < x[k + 1])

# ---------------------------------------------------------------------------
# 4. Constraints
# ---------------------------------------------------------------------------
# 4.1 All oranges must be in different bowls.
model.AddAllDifferent(x)

# 4.2 No three selected bowls may form an arithmetic progression.
#      For every triple i < j < k: 2 * x[j] != x[i] + x[k]
for i in range(NUM_ORANGES - 2):
    for j in range(i + 1, NUM_ORANGES - 1):
        for k in range(j + 1, NUM_ORANGES):
            model.Add(2 * x[j] != x[i] + x[k])

# ---------------------------------------------------------------------------
# 5. Objective – none (pure feasibility)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 6. Solve
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
# You may limit time if desired, e.g.:
# solver.parameters.max_time_in_seconds = 10
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = [solver.Value(var) for var in x]
    print(json.dumps({"x": solution}))
else:
    # According to the statement the instance is known to be solvable. If, for
    # any unexpected reason, no solution is found we emit an empty list so the
    # JSON output format is still respected.
    print(json.dumps({"x": []}))
