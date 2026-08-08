from cpmpy import *
import json
from itertools import combinations

# Parameters
n_bowls = 40  # Number of bowls
n_oranges = 9  # Number of oranges

# Decision variables
x = intvar(1, n_bowls, shape=n_oranges, name="x")

# Model
model = Model()

# All oranges must be in different bowls
model += [AllDifferent(x)]

# No three oranges A, B, and C such that the distance between A and B is equal to the distance between B and C
# This means no arithmetic progression of length 3
for a, b, c in combinations(range(n_oranges), 3):
    # Ensure that the three selected positions do not form an arithmetic progression
    model += [~((x[b] - x[a]) == (x[c] - x[b]))]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))