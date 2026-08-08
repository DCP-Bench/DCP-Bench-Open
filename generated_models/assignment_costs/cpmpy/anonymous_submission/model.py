# Import libraries
from cpmpy import *
import json

# Parameters
cost = [  # Cost matrix, rows are tasks, columns are people
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]
n_tasks = len(cost)
n_people = len(cost[0])

# Decision Variables
x = boolvar(shape=(n_tasks, n_people), name="x")  # Assignment matrix

# Model
model = Model()

# Each task must be assigned to exactly one person
model += [sum(x[t, :]) == 1 for t in range(n_tasks)]

# Total cost to minimize
total_cost = sum(x * cost)

# Objective: minimize total cost
model.minimize(total_cost)

# Solve
model.solve()

# Print solution
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script