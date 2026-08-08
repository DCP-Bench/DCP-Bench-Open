
import cpmpy as cp
import json

# Data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]  # Ratings of the children
# End of data

# Model definition
model = cp.Model()

n = len(ratings)
# Decision Variables: candies for each child, at least 1, at most n
c = cp.intvar(1, n, shape=n, name="c")

# Constraints:
# If a child has a higher rating than the next, they must get more candies, and vice versa
for i in range(n-1):
    if ratings[i] < ratings[i+1]:
        model += [c[i] < c[i+1]]
    elif ratings[i] > ratings[i+1]:
        model += [c[i] > c[i+1]]
    # if ratings are equal, no constraint

# Objective: minimize total number of candies
z = cp.sum(c)
model.minimize(z)

# Solve and print
if model.solve():
    solution = {'z': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
