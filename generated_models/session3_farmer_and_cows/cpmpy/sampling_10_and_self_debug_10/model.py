
import cpmpy as cp
import json

# Data
num_cows = 25
milk = list(range(1, num_cows + 1))  # milk production per cow (1 to 25)
num_sons = 5
sons_cow_counts = [7, 6, 5, 4, 3]  # number of cows per son

# Model definition
model = cp.Model()

# Decision Variables
# cow_assignments[i] in [0..4] indicates which son gets cow i
cow_assignments = cp.intvar(0, num_sons - 1, shape=num_cows, name="cow_assignments")

# Constraints
# Number of cows per son
for s in range(num_sons):
    model += (cp.Count(cow_assignments, s) == sons_cow_counts[s])

# Total milk per son must be equal
milk_per_son = []
for s in range(num_sons):
    # Sum milk for cows assigned to son s
    # Using element-wise multiplication and counting
    # sum of milk[i] for i where cow_assignments[i] == s
    milk_sum = cp.sum([milk[i] * (cow_assignments[i] == s) for i in range(num_cows)])
    milk_per_son.append(milk_sum)

# All sons should have the same total milk production
for s in range(1, num_sons):
    model += (milk_per_son[s] == milk_per_son[0])

# Solve and print
if model.solve():
    solution = {'cow_assignments': cow_assignments.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
