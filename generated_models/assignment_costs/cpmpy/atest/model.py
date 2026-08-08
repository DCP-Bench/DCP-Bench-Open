from cpmpy import *
import json

# Input data
cost = [
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]  # Cost matrix

# Number of tasks and people
num_tasks = len(cost)
num_people = len(cost[0])

# Decision variables
# x[i][j] = 1 if task i is assigned to person j, 0 otherwise
x = boolvar(shape=(num_tasks, num_people), name="x")

# Model
model = Model()

# Objective: minimize the total cost
total_cost = sum([cost[i][j] * x[i][j] for i in range(num_tasks) for j in range(num_people)])
model.minimize(total_cost)

# Each task must be assigned to exactly one person
for i in range(num_tasks):
    model += [sum(x[i, :]) == 1]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))