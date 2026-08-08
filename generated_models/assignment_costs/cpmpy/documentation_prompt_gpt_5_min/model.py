
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
# End of data

# Model definition
model = cp.Model()

# Decision Variables: x[i,j] is 1 if task i assigned to person j
x = cp.boolvar(shape=(num_tasks, num_people), name="x")

# Constraints: each task assigned to exactly one person
for i in range(num_tasks):
    model += cp.sum(x[i, :]) == 1

# Objective: minimize total cost
objective = cp.sum([cost[i][j] * x[i, j] for i in range(num_tasks) for j in range(num_people)])
model.minimize(objective)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
