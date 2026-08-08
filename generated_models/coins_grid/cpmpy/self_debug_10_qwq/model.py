
import cpmpy as cp
import json
import numpy as np  # Added for numpy array support

# Decision Variables
x = cp.boolvar(shape=(31, 31), name="x")

# Model initialization
model = cp.Model()

# Constraints for row sums (each row has exactly 14 coins)
for i in range(31):
    model += cp.sum(x[i, :]) == 14  # Sum over each row

# Constraints for column sums (each column has exactly 14 coins)
for j in range(31):
    model += cp.sum(x[:, j]) == 14  # Sum over each column

# Objective: minimize sum of squared horizontal distances from the main diagonal
# Convert distance_squared to a numpy array for element-wise multiplication
distance_squared = np.array([[(j - i)**2 for j in range(31)] for i in range(31)])
objective = cp.sum(x * distance_squared)  # Now valid with numpy array
model.minimize(objective)

# Solve and print
if model.solve():
    # Convert boolean values to 0/1 integers for JSON
    x_val = x.value().tolist()
    x_val = [[int(v) for v in row] for row in x_val]
    z = int(model.objective_value())
    solution = {'x': x_val, 'z': z}
    print(json.dumps(solution))
else:
    print("No solution found.")
