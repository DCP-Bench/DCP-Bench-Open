
import cpmpy as cp
import json
import numpy as np

# Precompute the squared distance matrix
distance_matrix = np.zeros((31, 31), dtype=int)
for i in range(31):
    for j in range(31):
        distance_matrix[i, j] = (i - j) ** 2

# Model definition
model = cp.Model()

# Decision variables: 31x31 grid of 0/1 (boolean) variables
x = cp.boolvar(shape=(31, 31), name="x")

# Constraints: Each row and column must have exactly 14 coins
for row in x:
    model += cp.sum(row) == 14  # Each row has 14 coins

for col in x.T:  # Iterate over columns (transposed matrix)
    model += cp.sum(col) == 14  # Each column has 14 coins

# Objective: Minimize the sum of squared distances from the main diagonal
total_distance = cp.sum(x * distance_matrix)
model.minimize(total_distance)

# Solve and print the solution
if model.solve():
    solution = {
        'x': x.value().tolist(),
        'z': int(model.objective_value())
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
