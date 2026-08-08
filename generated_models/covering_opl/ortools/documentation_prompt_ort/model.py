from ortools.sat.python import cp_model
import json

# Input data
nb_workers = 32  # Number of workers
num_tasks = 15  # Number of tasks
Qualified = [  # Which worker is qualified for each task (1-based indexing)
    [1, 9, 19, 22, 25, 28, 31],
    [2, 12, 15, 19, 21, 23, 27, 29, 30, 31, 32],
    [3, 10, 19, 24, 26, 30, 32], [4, 21, 25, 28, 32],
    [5, 11, 16, 22, 23, 27, 31], [6, 20, 24, 26, 30, 32],
    [7, 12, 17, 25, 30, 31], [8, 17, 20, 22, 23],
    [9, 13, 14, 26, 29, 30, 31], [10, 21, 25, 31, 32],
    [14, 15, 18, 23, 24, 27, 30, 32], [18, 19, 22, 24, 26, 29, 31],
    [11, 20, 25, 28, 30, 32], [16, 19, 23, 31],
    [9, 18, 26, 28, 31, 32]]
Cost = [  # Cost of hiring each worker
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5,
    5, 6, 6, 6, 7, 8, 9
]

# Model definition
model = cp_model.CpModel()

# Decision variables: workers[i] = 1 if worker i is selected, 0 otherwise
workers = [model.NewBoolVar(f'worker_{i}') for i in range(nb_workers)]

# Constraints: Each task must be performed by at least one qualified selected worker
for t in range(num_tasks):
    # Convert 1-based worker indices to 0-based
    qualified_workers = [w - 1 for w in Qualified[t]]
    # Sum of selected qualified workers for task t >= 1
    model.Add(sum(workers[w] for w in qualified_workers) >= 1)

# Objective: minimize total cost of selected workers
total_cost = model.NewIntVar(0, sum(Cost), 'total_cost')
model.Add(total_cost == sum(workers[i] * Cost[i] for i in range(nb_workers)))
model.Minimize(total_cost)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'total_cost': solver.Value(total_cost),
        'workers': [solver.Value(w) for w in workers]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")