
import cpmpy as cp
import json

# Data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]
n = len(ratings)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: candies for each child, at least 1 candy
candies = cp.intvar(1, 1000, shape=n, name="candies")  # upper bound large enough

# Constraints
for i in range(n - 1):
    if ratings[i] > ratings[i + 1]:
        model += candies[i] > candies[i + 1]
    elif ratings[i] < ratings[i + 1]:
        model += candies[i] < candies[i + 1]
    else:
        # If ratings are equal, no constraint on candies relative to neighbors
        pass

# Objective: minimize total candies
total_candies = cp.sum(candies)
model.minimize(total_candies)

# Solve and print
if model.solve():
    solution = {'z': int(total_candies.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
