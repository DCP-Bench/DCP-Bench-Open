
import cpmpy as cp
import json

# Data
num_people = 8
compatible = [
    [2,3],
    [1,6],
    [1,4,7],
    [2],
    [2],
    [5],
    [8],
    [3]
]

# Convert compatible to 0-based indices
compatible = [[x-1 for x in sublist] for sublist in compatible]

# Model definition
model = cp.Model()

# Decision Variables
transplants = cp.boolvar(shape=(num_people, num_people), name="transplants")

# Constraints
# Compatibility constraints: transplants[i][j] can only be 1 if j is in compatible[i]
for i in range(num_people):
    for j in range(num_people):
        if j not in compatible[i]:
            model += transplants[i, j] == 0

# Each person donates at most once
model += [cp.sum(transplants[i, :]) <= 1 for i in range(num_people)]

# Each person receives at most once
model += [cp.sum(transplants[:, j]) <= 1 for j in range(num_people)]

# For each person, donations equal receptions
model += [cp.sum(transplants[i, :]) == cp.sum(transplants[:, i]) for i in range(num_people)]

# Objective: maximize the total number of transplants
model.maximize(cp.sum(transplants))

# Solve and print
if model.solve():
    transplants_val = transplants.value().tolist()
    solution = {'transplants': transplants_val}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
