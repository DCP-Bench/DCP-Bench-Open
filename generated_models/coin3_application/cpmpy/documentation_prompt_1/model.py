
import cpmpy as cp
import json

# Data
denominations = [1, 2, 5, 10, 20, 50]
max_amount = 99  # amounts smaller than one Euro (1 to 99 cents)

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = number of coins of denomination denominations[i]
x = cp.intvar(0, max_amount, shape=len(denominations), name="x")

# Constraints
# For every amount from 1 to 99, it must be possible to pay exactly using the coins chosen
# We model this by introducing auxiliary variables y[a][i] = number of coins of denomination i used to pay amount a
y = cp.intvar(0, max_amount, shape=(max_amount, len(denominations)), name="y")

# For each amount a, sum of y[a][i]*denominations[i] == a+1 (since a in 0..98 means amount a+1)
for a in range(max_amount):
    model += (cp.sum([y[a, i] * denominations[i] for i in range(len(denominations))]) == a + 1)
    # The number of coins used for amount a cannot exceed the coins available
    for i in range(len(denominations)):
        model += (y[a, i] <= x[i])

# Objective: minimize total number of coins
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
