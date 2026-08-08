
import cpmpy as cp
import json

# Data
n_cows = 25
n_sons = 5
cow_weights = list(range(1, n_cows + 1))  # 1..25
sizes = [7, 6, 5, 4, 3]  # number of cows per son
target_sum = sum(cow_weights) // n_sons  # 325 / 5 = 65

# Model definition
model = cp.Model()

# Decision Variables
# b[k,i] = 1 if cow i (index 0..24) is assigned to son k (0..4)
b = cp.boolvar(shape=(n_sons, n_cows), name="b")
# Also create the assignment array as required for output
cow_assignments = cp.intvar(0, n_sons - 1, shape=n_cows, name="cow_assignments")

# Constraints

# Each cow is assigned to exactly one son and link b to cow_assignments
for i in range(n_cows):
    model += cp.sum([b[k, i] for k in range(n_sons)]) == 1
    # cow_assignments[i] equals the index k of the true b[k,i]
    model += cow_assignments[i] == cp.sum([k * b[k, i] for k in range(n_sons)])

# Each son gets the specified number of cows and the total milk equals target_sum
for k in range(n_sons):
    model += cp.sum([b[k, i] for i in range(n_cows)]) == sizes[k]
    model += cp.sum([cow_weights[i] * b[k, i] for i in range(n_cows)]) == target_sum

# Solve and print
if model.solve():
    solution = {'cow_assignments': cow_assignments.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
