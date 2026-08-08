
import cpmpy as cp
import json

# Define variables for the number of each coin type (1,2,5,10,20,50 cents)
x1, x2, x5, x10, x20, x50 = cp.intvar(0, 100, shape=6)

model = cp.Model()

# Constraints based on the greedy algorithm's requirements to cover all amounts 1-99
model += x1 >= 1         # At least 1 of 1c
model += x2 >= 2         # At least 2 of 2c
model += x5 >= 1         # At least 1 of 5c
model += x10 >= 1        # At least 1 of 10c
model += x20 >= 2        # At least 2 of 20c
model += x50 >= 1        # At least 1 of 50c

# Objective: minimize the total number of coins
model.minimize(x1 + x2 + x5 + x10 + x20 + x50)

if model.solve():
    solution = {
        'x': [int(x1.value()), int(x2.value()), int(x5.value()), 
              int(x10.value()), int(x20.value()), int(x50.value())]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
