
import cpmpy as cp
import json

cost = [
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]

model = cp.Model()

# Decision Variables: 4 tasks (rows) x 5 people (columns)
x = cp.boolvar(shape=(4, 5), name="x")

# Constraints: Each task (row) must be assigned to exactly one person
for task_row in x:
    model += (cp.sum(task_row) == 1)

# Objective: Minimize total cost
total_cost = cp.sum(x[i, j] * cost[i][j] for i in range(4) for j in range(5))
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
