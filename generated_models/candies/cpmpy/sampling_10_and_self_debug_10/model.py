
import cpmpy as cp
import json

# Data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]
n = len(ratings)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# candies[i]: number of candies given to child i, at least 1
candies = cp.intvar(1, n, shape=n, name="candies")

# Constraints
for i in range(n - 1):
    if ratings[i] > ratings[i + 1]:
        # left child has higher rating, must have more candies
        model += candies[i] > candies[i + 1]
    elif ratings[i] < ratings[i + 1]:
        # right child has higher rating, must have more candies
        model += candies[i] < candies[i + 1]
    else:
        # equal rating, no constraint on candies
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
