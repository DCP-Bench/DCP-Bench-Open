
import cpmpy as cp
import json

# Data
n = 12
max_triplet_sum = 21
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(1, n, shape=n, name="x")  # arrangement around the clock
s = cp.intvar(6, 33, shape=n, name="s")  # sums of each triplet of adjacent numbers

# Constraints
model += cp.AllDifferent(x)

# Symmetry breaking to reduce equivalent rotations/reflections
model += (x[0] == 1)
model += (x[1] < x[-1])

# Define triplet sums (circular adjacency) and enforce the maximum sum constraint
for i in range(n):
    model += (s[i] == x[i] + x[(i+1) % n] + x[(i+2) % n])
    model += (s[i] <= max_triplet_sum)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
