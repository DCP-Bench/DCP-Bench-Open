
import cpmpy as cp
import json
import numpy as np

# Data
n_cows = 25
sons = 5
weights = np.arange(1, n_cows + 1)  # milk yields 1..25
counts = [7, 6, 5, 4, 3]  # cows per son (sons indexed 0..4)
target_sum = int((n_cows * (n_cows + 1)) // 2 // sons)  # total milk per son = 325/5 = 65

# Model definition
model = cp.Model()

# Decision Variables
# cow_assignments[i] in {0..4} is the son index for cow i (0-based)
cow_assignments = cp.intvar(0, sons - 1, shape=n_cows, name="cow_assignments")

# Constraints
# 1) Each son gets the required number of cows
for s in range(sons):
    model += (cp.Count(cow_assignments, s) == counts[s])

# 2) Each son gets the same total milk (65)
for s in range(sons):
    model += (cp.sum([weights[i] * (cow_assignments[i] == s) for i in range(n_cows)]) == target_sum)

# Solve and print
if model.solve():
    solution = {
        'cow_assignments': cow_assignments.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
