
import cpmpy as cp
import json

# Data
num_cows = 25
milk = list(range(1, num_cows + 1))  # milk production per cow: 1 to 25
num_sons = 5
cows_per_son = [7, 6, 5, 4, 3]  # number of cows per son

# Model definition
model = cp.Model()

# Decision Variables
# cow_assignments[i] = j means cow i assigned to son j (0-based)
cow_assignments = cp.intvar(0, num_sons - 1, shape=num_cows, name="cow_assignments")

# Constraints

# Each son gets exactly the specified number of cows
for son in range(num_sons):
    model += (cp.Count(cow_assignments, son) == cows_per_son[son])

# The total milk per son must be equal
# Compute milk sums per son
milk_per_son = []
for son in range(num_sons):
    # sum of milk[i] for cows assigned to son
    milk_sum = cp.intvar(0, sum(milk), name=f"milk_sum_{son}")
    model += (milk_sum == cp.sum([milk[i] * (cow_assignments[i] == son) for i in range(num_cows)]))
    milk_per_son.append(milk_sum)

# All milk sums are equal
for son in range(1, num_sons):
    model += (milk_per_son[son] == milk_per_son[0])

# Solve and print
if model.solve():
    solution = {'cow_assignments': cow_assignments.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
