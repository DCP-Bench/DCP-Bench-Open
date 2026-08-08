from cpmpy import *
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
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5,
    5, 6, 6, 6, 7, 8, 9
]

# Decision variables
# workers[i] = 1 if worker i is selected, 0 otherwise
workers = boolvar(shape=nb_workers, name="workers")

# Model
model = Model()

# Objective: minimize the total cost
total_cost = sum([Cost[i] * workers[i] for i in range(len(Cost))])
model.minimize(total_cost)

# Each task must be assigned to at least one qualified worker
for task in range(num_tasks):
    qualified_workers = [i for i in range(nb_workers) if (i + 1) in Qualified[task]]
    model += [sum([workers[i] for i in qualified_workers]) >= 1]

# Solve the model
model.solve()

# Print the solution
solution = {
    "total_cost": total_cost.value(),
    "workers": workers.value().tolist()
}
print(json.dumps(solution))