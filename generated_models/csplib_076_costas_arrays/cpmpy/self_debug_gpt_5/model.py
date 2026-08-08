
import cpmpy as cp
import json

# Data (optional)
n = 8  # Size of the Costas array
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# costas[i] is the column position (1..n) of the mark in row i (0-based rows, 1-based values)
costas = cp.intvar(1, n, shape=n, name="costas")

# Constraints
# 1) Permutation constraint: one mark per column
model += cp.AllDifferent(costas)

# 2) Difference triangle constraints: for each lag l, the differences must be all different
for l in range(1, n):
    # Use a tuple for shape to ensure an array is created across environments
    diffs_l = cp.intvar(-(n-1), (n-1), shape=(n - l,), name=f"diffs_{l}")
    # Define the differences Xi - X_{i+l}
    for i in range(n - l):
        model += (diffs_l[i] == costas[i] - costas[i + l])
    # Enforce all-different within this lag line
    model += cp.AllDifferent(diffs_l)

# (Optional) Mild symmetry breaking to speed up search
model += (costas[0] < costas[n - 1])

# Objective (none) - feasibility problem

# Solve and print
if model.solve():
    solution = {'costas': costas.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
