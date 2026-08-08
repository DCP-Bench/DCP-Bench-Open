
import cpmpy as cp
import json

# Data
num_people = 8  # number of people
compatible = [  # 1-based indexing, compatible[i] is the list of people to which i can donate
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
]
# convert to 0-based indexing
compatible0 = [[j-1 for j in donors] for donors in compatible]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: transplants[i][j] = 1 if i donates to j
transplants = cp.boolvar(shape=(num_people, num_people), name="transplants")

# Constraints
# 1) Only allow transplants where compatible
for i in range(num_people):
    for j in range(num_people):
        if j not in compatible0[i]:
            model += (transplants[i, j] == 0)

# 2) For each person i: sum of out-transplants == sum of in-transplants (either 0 or 1)
# and sum of out-transplants <= 1
for i in range(num_people):
    out_i = cp.sum(transplants[i, :])
    in_i = cp.sum(transplants[:, i])
    model += (out_i == in_i)
    model += (out_i <= 1)

# Objective: maximize total number of transplants
model.maximize(cp.sum(transplants))

# Solve and print
if model.solve():
    solution = {
        'transplants': transplants.value().tolist()
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
