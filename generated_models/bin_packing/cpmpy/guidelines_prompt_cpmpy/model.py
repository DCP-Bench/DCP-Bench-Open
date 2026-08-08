
import cpmpy as cp
import json

# Data
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
n = len(weights)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# x[i,b] = 1 if item i is placed in bin b
x = cp.BoolVar(shape=(n, num_bins), name="x")
# bins[i] is the bin index assigned to item i
bins = cp.IntVar(0, num_bins-1, shape=n, name="bins")

# Constraints
# Each item must go to exactly one bin
for i in range(n):
    model += (cp.sum(x[i, :]) == 1)

# Capacity constraint for each bin
for b in range(num_bins):
    model += (cp.sum([weights[i] * x[i, b] for i in range(n)]) <= capacity)

# Link bins[i] with x[i,b]
for i in range(n):
    model += (cp.sum([b * x[i, b] for b in range(num_bins)]) == bins[i])

# Solve and print
if model.solve():
    solution = {'bins': bins.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
