
import cpmpy as cp
import json

# Data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]  # Ratings of the children
n = len(ratings)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: at least 1 candy, upper bound n is safe
x = cp.intvar(1, n, shape=n, name="x")

# Constraints:
# If a child has higher rating than an immediate neighbor, they must get more candies.
for i in range(n - 1):
    if ratings[i] > ratings[i + 1]:
        model += x[i] > x[i + 1]
    elif ratings[i] < ratings[i + 1]:
        model += x[i] < x[i + 1]
    # if equal, no constraint between them

# Objective: minimize total candies
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {
        'z': int(model.objective_value()),
        'x': x.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
