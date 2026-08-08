import json
from ortools.sat.python import cp_model

# ----------------------
# 1. Input data (immutable)
# ----------------------
# Cost matrix: rows = tasks (4), columns = people (5)
cost = [
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]

num_tasks = len(cost)          # 4
num_people = len(cost[0])      # 5

# ----------------------
# 2. Model creation
# ----------------------
model = cp_model.CpModel()

# Decision variables: x[t][p] = 1 if task t is assigned to person p
x = [[model.NewBoolVar(f"x[{t}][{p}]") for p in range(num_people)]
     for t in range(num_tasks)]

# ----------------------
# 3. Constraints
# ----------------------
# Each task must be assigned to exactly one person
for t in range(num_tasks):
    model.Add(sum(x[t][p] for p in range(num_people)) == 1)

# ----------------------
# 4. Objective: minimize total cost
# ----------------------
model.Minimize(
    sum(cost[t][p] * x[t][p] for t in range(num_tasks) for p in range(num_people))
)

# ----------------------
# 5. Solve
# ----------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safe guard; optional
status = solver.Solve(model)

# ----------------------
# 6. Extract solution
# ----------------------
solution_x = []
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    for t in range(num_tasks):
        row = []
        for p in range(num_people):
            row.append(int(solver.Value(x[t][p])))
        solution_x.append(row)
else:
    # No feasible assignment found; still comply with output format
    solution_x = [[0 for _ in range(num_people)] for _ in range(num_tasks)]

# ----------------------
# 7. Output result as JSON
# ----------------------
print(json.dumps({"x": solution_x}))
