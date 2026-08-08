# Import libraries
from cpmpy import *
import json

# Parameters
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

# Decision Variables
workers = boolvar(shape=nb_workers, name="workers")  # Whether each worker is selected
total_cost = intvar(0, sum(Cost), name="total_cost")  # Total hiring cost

# Model
model = Model()

# Constraint: all tasks must be performed by at least one qualified worker
for task in range(num_tasks):
    qualified_workers = [workers[w-1] for w in Qualified[task]]  # Convert to 0-based index
    model += sum(qualified_workers) >= 1

# Calculate total cost
model += total_cost == sum(workers * Cost)

# Objective: minimize total cost
model.minimize(total_cost)

# Solve
model.solve()

# Print solution
solution = {
    "total_cost": total_cost.value(),
    "workers": workers.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script