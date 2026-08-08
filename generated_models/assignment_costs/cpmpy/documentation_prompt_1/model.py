
import cpmpy as cp
import json

# Data
cost = [  # Cost matrix, rows are tasks, columns are people
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]

num_tasks = len(cost)
num_people = len(cost[0])

# Model definition
model = cp.Model()

# Decision Variables
# x[t, p] = 1 if task t is assigned to person p, else 0
x = cp.boolvar(shape=(num_tasks, num_people), name="x")

# Constraints
# Each task must be assigned to exactly one person
for t in range(num_tasks):
    model += (cp.sum(x[t, :]) == 1)

# Objective: minimize total cost
total_cost = cp.sum([x[t, p] * cost[t][p] for t in range(num_tasks) for p in range(num_people)])
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {'x': x.value().astype(int).tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
