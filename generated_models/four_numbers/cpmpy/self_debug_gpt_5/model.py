
import cpmpy as cp
import json

# Data (optional)
numbers = [7, 8, 9, 10]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(1, 10, shape=3, name="x")  # three integers between 1 and 10

# Symmetry breaking (optional): non-decreasing order
model += cp.Increasing(x)

# For each target number, create subset selection booleans and enforce subset-sum equality
for idx, t in enumerate(numbers):
    b = cp.boolvar(shape=3, name=f"b_{idx}")  # subset selection for this target
    # Ensure the subset is non-empty and sums to the target t
    model += (cp.sum(b) >= 1)
    model += (cp.sum([b[i] * x[i] for i in range(3)]) == t)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
