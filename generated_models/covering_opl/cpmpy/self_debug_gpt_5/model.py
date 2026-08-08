
import cpmpy as cp
import json
import numpy as np

# Data (optional)
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
    [9, 18, 26, 28, 31, 32]
]
Cost = [  # Cost of hiring each worker
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5,
    5, 6, 6, 6, 7, 8, 9
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
workers = cp.boolvar(shape=nb_workers, name="workers")

# Constraints
# Ensure each task is covered by at least one qualified hired worker
for t in range(num_tasks):
    qualified_indices = [w - 1 for w in Qualified[t]]  # convert to 0-based
    model += (cp.sum([workers[w] for w in qualified_indices]) >= 1)

# Objective (optional)
total_cost_expr = cp.sum([Cost[i] * workers[i] for i in range(nb_workers)])
model.minimize(total_cost_expr)

# Solve and print
if model.solve():
    solution = {
        'total_cost': int(model.objective_value()),
        'workers': np.array(workers.value(), dtype=int).tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
