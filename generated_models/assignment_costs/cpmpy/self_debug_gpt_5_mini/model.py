
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
    # Convert boolean matrix to integers 0/1 for JSON output
    x_vals_bool_list = x.value().tolist()
    x_vals_int_list = [[int(v) for v in row] for row in x_vals_bool_list]
    solution = {'x': x_vals_int_list}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
