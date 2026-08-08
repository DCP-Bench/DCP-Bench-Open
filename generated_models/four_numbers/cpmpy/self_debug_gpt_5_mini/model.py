
import cpmpy as cp
import json

# Data
numbers = [7, 8, 9, 10]
m = len(numbers)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: three integers between 1 and 10
x = cp.intvar(1, 10, shape=3, name="x")

# For each given number, a boolean selection of which of the three x's are used in the subset sum
sel = cp.boolvar(shape=(m, 3), name="sel")

# Constraints
for k in range(m):
    # The weighted sum of selected x's must equal the given number
    model += (cp.sum(sel[k] * x) == numbers[k])
    # At least one element must be selected (non-empty subset)
    model += (cp.sum(sel[k]) >= 1)

# Symmetry breaking: enforce non-decreasing order on x to reduce equivalent permutations
model += cp.Increasing(x)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
