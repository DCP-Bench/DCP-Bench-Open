
import cpmpy as cp
import json

# Data
cow_values = list(range(1, 26))  # Cow numbers 1 to 25
counts = [7, 6, 5, 4, 3]        # Cows per son (0 to 4)

# Model
model = cp.Model()

# Decision Variables
cow_assignments = cp.intvar(0, 4, shape=25, name="cow_assignments")

# Constraints for the number of cows each son receives
for i in range(5):
    model += (cp.Count(cow_assignments, i) == counts[i])

# Constraints for equal milk production (65 kg per son)
for i in range(5):
    terms = [cow_values[j] * (cow_assignments[j] == i) for j in range(25)]
    model += (cp.sum(terms) == 65)

# Solve and print
if model.solve():
    solution = {'cow_assignments': cow_assignments.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
