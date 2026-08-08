# Import libraries
from cpmpy import *
import json

# Parameters
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]  # Ratings of the children
n = len(ratings)

# Decision Variables
candies = intvar(1, 100, shape=n, name="candies")  # Candies for each child
z = intvar(1, 100*n, name="z")  # Total number of candies

# Model
model = Model()

# Each child gets at least 1 candy
model += [candies[i] >= 1 for i in range(n)]

# Children with higher ratings get more candies than their neighbors
for i in range(n-1):
    if ratings[i] > ratings[i+1]:
        model += candies[i] > candies[i+1]
    elif ratings[i] < ratings[i+1]:
        model += candies[i] < candies[i+1]

# Total candies to minimize
model += z == sum(candies)

# Objective: minimize total candies
model.minimize(z)

# Solve
model.solve()

# Print solution
solution = {
    "z": z.value(),
    "x": candies.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script