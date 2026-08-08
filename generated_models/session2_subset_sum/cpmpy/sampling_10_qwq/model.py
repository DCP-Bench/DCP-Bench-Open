
import cpmpy as cp
import json

coins = [16, 17, 23, 24, 39, 40]
upper_bounds = [100 // c for c in coins]

model = cp.Model()

# Decision variables for each coin type's stolen bags
x = [cp.intvar(0, ub, name=f"x{c}") for c, ub in zip(coins, upper_bounds)]

# Constraint: Total coins stolen must be exactly 100
model += cp.sum([x[i] * coins[i] for i in range(len(coins))]) == 100

# Solve and print the solution
if model.solve():
    solution = {'bags': [int(v.value()) for v in x]}
    print(json.dumps(solution))
else:
    print("No solution found.")
