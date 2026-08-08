
import cpmpy as cp
import json

# Data
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
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# workers[i] = 1 if worker i is selected, else 0
workers = cp.boolvar(shape=nb_workers, name="workers")

# Constraints
# For each task, at least one qualified worker must be selected
for t in range(num_tasks):
    # Convert 1-based indexing to 0-based
    qualified_workers = [w-1 for w in Qualified[t]]
    model += cp.sum(workers[qualified_workers]) >= 1

# Objective: minimize total cost of selected workers
total_cost = cp.sum([workers[i] * Cost[i] for i in range(nb_workers)])
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {
        'total_cost': int(model.objective_value()),
        'workers': workers.value().astype(int).tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
