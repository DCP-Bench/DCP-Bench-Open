
import cpmpy as cp
import json

# Data
counts = [7, 6, 5, 4, 3]       # number of cows per son
milk = list(range(1, 26))      # milk production for cows 1..25

# Model definition
model = cp.Model()

# Decision Variables
# cow_assignments[j] = i means cow j (0-based index) is assigned to son i (0..4)
cow_assignments = cp.intvar(0, 4, shape=25, name="cow_assignments")

# Constraints
# 1) Each son i receives exactly counts[i] cows
for i in range(5):
    model += cp.sum([cow_assignments[j] == i for j in range(25)]) == counts[i]

# 2) Each son produces the same total milk
#    Compute milk sum for each son
sum_milk = []
for i in range(5):
    sum_i = cp.sum([(cow_assignments[j] == i) * milk[j] for j in range(25)])
    sum_milk.append(sum_i)
#    Enforce equality of all sums to sum_milk[0]
for i in range(1, 5):
    model += sum_milk[i] == sum_milk[0]

# Solve and print
if model.solve():
    solution = {
        'cow_assignments': cow_assignments.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
