
import cpmpy as cp
import json

# Data
cost = [  # Cost matrix, rows are tasks, columns are people
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]
# End of data

# Model definition
model = cp.Model()

# Dimensions
m = len(cost)       # number of tasks
n = len(cost[0])    # number of people

# Decision Variables: x[i,j] = 1 if task i is assigned to person j
x = cp.boolvar(shape=(m, n), name="x")

# Constraints
# Each task must be assigned to exactly one person
for i in range(m):
    model += cp.sum(x[i, :]) == 1

# Objective: minimize total cost
objective = cp.sum([cost[i][j] * x[i, j] for i in range(m) for j in range(n)])
model.minimize(objective)

# Solve and print
if model.solve():
    # Convert boolean matrix to list of lists of 0/1 integers
    x_vals = x.value().tolist()
    x_int = [[int(v) for v in row] for row in x_vals]
    solution = {'x': x_int}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
