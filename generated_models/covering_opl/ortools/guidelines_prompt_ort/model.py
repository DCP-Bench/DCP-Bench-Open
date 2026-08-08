
from ortools.sat.python import cp_model
import json

# Input data
nb_workers = 32  # Number of workers
num_tasks = 15  # Number of tasks
Qualified = [  # Which worker is qualified for each task (1-based indexing)
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
Cost = [  # Cost of hiring each worker
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5,
    5, 6, 6, 6, 7, 8, 9
]

# Model definition
model = cp_model.CpModel()

# Decision Variables: workers[i] == 1 if worker i is selected, else 0
workers = [model.NewBoolVar(f'worker_{i}') for i in range(nb_workers)]

# Constraints: each task must be covered by at least one selected worker
for t in range(num_tasks):
    # Convert 1-based indices in Qualified to 0-based
    model.Add(
        sum(workers[w-1] for w in Qualified[t]) >= 1
    )

# Objective: minimize total hiring cost
model.Minimize(sum(Cost[i] * workers[i] for i in range(nb_workers)))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    selected_workers = [solver.Value(workers[i]) for i in range(nb_workers)]
    total_cost = sum(Cost[i] * selected_workers[i] for i in range(nb_workers))
    solution = {
        'total_cost': total_cost,
        'workers': selected_workers
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
