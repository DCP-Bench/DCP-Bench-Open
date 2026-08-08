# Complete, runnable Python code that solves the worker-selection problem
# ---------------------------------------------------------------
# 1. Imports
import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------
# 2. Input data (exactly as provided)
nb_workers = 32  # Number of workers
num_tasks = 15   # Number of tasks
Qualified = [    # Workers qualified for each task (1-based indexing)
    [1, 9, 19, 22, 25, 28, 31],
    [2, 12, 15, 19, 21, 23, 27, 29, 30, 31, 32],
    [3, 10, 19, 24, 26, 30, 32],
    [4, 21, 25, 28, 32],
    [5, 11, 16, 22, 23, 27, 31],
    [6, 20, 24, 26, 30, 32],
    [7, 12, 17, 25, 30, 31],
    [8, 17, 20, 22, 23],
    [9, 13, 14, 26, 29, 30, 31],
    [10, 21, 25, 31, 32],
    [14, 15, 18, 23, 24, 27, 30, 32],
    [18, 19, 22, 24, 26, 29, 31],
    [11, 20, 25, 28, 30, 32],
    [16, 19, 23, 31],
    [9, 18, 26, 28, 31, 32]
]
Cost = [  # Hiring cost of each worker
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2,
    3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 8, 9
]

# ---------------------------------------------------------------
# 3. Model construction
model = cp_model.CpModel()

# Decision variables: workers[i] == 1 if worker i is hired (0-based index)
workers = [model.NewBoolVar(f"worker_{i+1}") for i in range(nb_workers)]

# total_cost variable explicitly defined for clarity (optional but matches spec)
max_total_cost = sum(Cost)
total_cost = model.NewIntVar(0, max_total_cost, "total_cost")

# ---------------------------------------------------------------
# 4. Constraints
# 4.1 Coverage: every task must be covered by at least one selected worker
for task_idx in range(num_tasks):
    qualified_workers = [workers[w-1] for w in Qualified[task_idx]]  # convert to 0-based indices
    model.Add(sum(qualified_workers) >= 1)

# 4.2 Cost definition: link total_cost with selected workers
model.Add(total_cost == sum(Cost[i] * workers[i] for i in range(nb_workers)))

# ---------------------------------------------------------------
# 5. Objective: minimize total_cost
model.Minimize(total_cost)

# ---------------------------------------------------------------
# 6. Solve the model
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # optional time limit
status = solver.Solve(model)

# ---------------------------------------------------------------
# 7. Extract and print solution as JSON
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution_cost = int(solver.Value(total_cost))
    solution_workers = [int(solver.Value(w)) for w in workers]
    result = {"total_cost": solution_cost, "workers": solution_workers}
    print(json.dumps(result))
else:
    # Infeasible or unknown status – still output a JSON object indicating failure
    print(json.dumps({"total_cost": None, "workers": []}))
