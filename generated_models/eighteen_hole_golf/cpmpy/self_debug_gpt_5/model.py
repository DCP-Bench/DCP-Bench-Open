
import cpmpy as cp
import json
import numpy as np

# Data
n_holes = 18
total_length = 72
rng = np.random.default_rng()

# Model definition
model = cp.Model()

# Decision Variables
holes = cp.intvar(3, 5, shape=n_holes, name="holes")

# Constraints
model += (cp.sum(holes) == total_length)

# Objective: use random weights to get a "random" feasible solution
weights = rng.integers(1, 100, size=n_holes).tolist()
objective = cp.sum([weights[i] * holes[i] for i in range(n_holes)])
model.maximize(objective)

# Solve and print
if model.solve():
    solution = {'holes': holes.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
