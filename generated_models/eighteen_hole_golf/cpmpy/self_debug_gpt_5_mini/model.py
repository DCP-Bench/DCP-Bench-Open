
import cpmpy as cp
import json
import random

# Data
n_holes = 18
min_len = 3
max_len = 5
total_length = 72

# Model definition
model = cp.Model()

# Decision Variables: 18 holes with lengths 3,4,5
holes = cp.intvar(min_len, max_len, shape=n_holes, name="holes")

# Constraints: total length equals 72
model += (cp.sum(holes) == total_length)

# To get a "random" valid course (instead of the trivial all-4 solution),
# add a randomized linear objective that biases the solver.
# This does not change the feasibility region, only which solution is returned.
random_weights = [random.randint(1, 100) for _ in range(n_holes)]
model.maximize(cp.sum([random_weights[i] * holes[i] for i in range(n_holes)]))

# Solve and print
if model.solve():
    solution = {'holes': holes.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
