
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
# workers[i] == 1 if worker i (0-based) is hired, else 0
workers = cp.boolvar(shape=nb_workers, name="workers")

# Constraints
# Each task must be performed by at least one qualified worker
for task_quals in Qualified:
    # task_quals contains 1-based worker indices; convert to 0-based
    model += cp.sum([workers[w - 1] for w in task_quals]) >= 1

# Objective: minimize total hiring cost
total_cost_expr = cp.sum([Cost[i] * workers[i] for i in range(nb_workers)])
model.minimize(total_cost_expr)

# Solve and print
if model.solve():
    # Convert boolean values to 0/1 integers as required
    workers_list = [int(v) for v in workers.value().tolist()]
    solution = {
        'total_cost': int(model.objective_value()),
        'workers': workers_list
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
