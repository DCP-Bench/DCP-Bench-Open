
import cpmpy as cp
import json

# Data
n = 4
price = [50, 20, 30, 80]  # in cents
limits = [500, 6, 10, 8]  # requirements: Calories, Chocolate(oz), Sugar(oz), Fat(oz)

# Nutrition per food (rows: foods, cols: nutrition types)
# Chocolate Cake, Chocolate ice cream, Cola, Pineapple cheesecake
nutrition = [
    [400, 3, 2, 2],
    [200, 2, 2, 4],
    [150, 0, 4, 1],
    [500, 0, 4, 5]
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: number of servings of each food (integer, >=0)
x = cp.intvar(0, 100, shape=n, name="x")  # upper bound 100 is a safe arbitrary bound

# Constraints: meet or exceed nutritional requirements
# Calories
model += cp.sum([nutrition[i][0] * x[i] for i in range(n)]) >= limits[0]
# Chocolate (ounces)
model += cp.sum([nutrition[i][1] * x[i] for i in range(n)]) >= limits[1]
# Sugar (ounces)
model += cp.sum([nutrition[i][2] * x[i] for i in range(n)]) >= limits[2]
# Fat (ounces)
model += cp.sum([nutrition[i][3] * x[i] for i in range(n)]) >= limits[3]

# Objective: minimize total cost
model.minimize(cp.sum([price[i] * x[i] for i in range(n)]))

# Solve and print
if model.solve():
    solution = {'cost': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
