
import cpmpy as cp
import json

# Data (optional)
n = 4
price = [50, 20, 30, 80]  # in cents
limits = [500, 6, 10, 8]  # [Calories, Chocolate, Sugar, Fat] minimum requirements

# Nutrition content per food item
calories = [400, 200, 150, 500]
chocolate = [3, 2, 0, 0]
sugar = [2, 2, 4, 4]
fat = [2, 4, 1, 5]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: number of units for each food item (non-negative integers)
# Upper bound set to a reasonable large number to ensure feasibility
x = cp.intvar(0, 100, shape=n, name="x")

# Constraints
model += (cp.sum([calories[i] * x[i] for i in range(n)]) >= limits[0])  # Calories
model += (cp.sum([chocolate[i] * x[i] for i in range(n)]) >= limits[1]) # Chocolate
model += (cp.sum([sugar[i] * x[i] for i in range(n)]) >= limits[2])     # Sugar
model += (cp.sum([fat[i] * x[i] for i in range(n)]) >= limits[3])       # Fat

# Objective (minimize total cost)
objective = cp.sum([price[i] * x[i] for i in range(n)])
model.minimize(objective)

# Solve and print
if model.solve():
    solution = {'cost': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
