
import cpmpy as cp
import json

# Data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]  # Ratings of the children
n = len(ratings)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(1, n, shape=n, name="x")  # candies for each child, at least 1, at most n

# Constraints
# Neighbor constraints based on ratings
for i in range(n - 1):
    if ratings[i] < ratings[i + 1]:
        model += (x[i] < x[i + 1])
    elif ratings[i] > ratings[i + 1]:
        model += (x[i] > x[i + 1])
    # equal ratings: no constraint between neighbors

# Objective: minimize total candies
total_candies = cp.sum(x)
model.minimize(total_candies)

# Solve and print
if model.solve():
    solution = {
        'z': int(model.objective_value()),
        'x': x.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
