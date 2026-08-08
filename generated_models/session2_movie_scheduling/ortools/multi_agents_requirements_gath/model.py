import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# Fixed input data (must not be altered)
# ---------------------------------------------------------------------------
movies = [  # title, start, end
    ["Tarjan of the Jungle", 4, 13],
    ["The Four Volume Problem", 17, 27],
    ["The President's Algorist", 1, 10],
    ["Steiner's Tree", 12, 18],
    ["Process Terminated", 23, 30],
    ["Halting State", 9, 16],
    ["Programming Challenges", 19, 25],
    ["Discrete Mathematics", 2, 7],
    ["Calculated Bets", 26, 31],
]

n = len(movies)
start = [m[1] for m in movies]
end = [m[2] for m in movies]

# ---------------------------------------------------------------------------
# Build conflict pairs (i, j) with i < j whenever intervals overlap (inclusive)
# ---------------------------------------------------------------------------
conflict_pairs = []
for i in range(n):
    for j in range(i + 1, n):
        if start[i] <= end[j] and start[j] <= end[i]:
            conflict_pairs.append((i, j))

# ---------------------------------------------------------------------------
# CP-SAT model
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Binary decision variables: x[i] == 1 if movie i is accepted
x = [model.NewBoolVar(f"x_{i}") for i in range(n)]

# Total number of accepted movies
num_selected = model.NewIntVar(0, n, "num_selected")
model.Add(num_selected == sum(x))

# Non-overlap constraints
for i, j in conflict_pairs:
    model.Add(x[i] + x[j] <= 1)

# Objective: maximise the number of accepted movies
model.Maximize(num_selected)

# ---------------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 8  # use available cores
status = solver.Solve(model)

# ---------------------------------------------------------------------------
# Output results as JSON with mandatory keys
# ---------------------------------------------------------------------------
if status == cp_model.OPTIMAL:
    selected_movies = [int(solver.Value(var)) for var in x]
    result = {
        "in the order of the input list": True,
        "selected_movies": selected_movies,
        "num_selected_movies": int(solver.Value(num_selected)),
    }
else:
    # No optimal solution found (should not occur for this tiny instance).
    result = {
        "in the order of the input list": True,
        "selected_movies": [0] * n,
        "num_selected_movies": 0,
    }

print(json.dumps(result))
