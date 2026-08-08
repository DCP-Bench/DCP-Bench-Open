
import cpmpy as cp
import json

# Data: coin denominations in cents
coins = [1, 2, 5, 10, 20, 50]

# Model definition
model = cp.Model()

# Decision variables: number of each coin type used
x = cp.intvar(0, 100, shape=len(coins), name="x")

# We want to be able to pay exactly any amount from 1 to 99 cents
# For each amount, there must be a way to pay it exactly using the chosen coins.
# We model this by introducing auxiliary variables for each amount and coin count.

# For each amount, define auxiliary variables: how many of each coin to use
pay = []
for amount in range(1, 100):
    # For each coin type, number used to pay this amount, max could be amount//coin value
    pay_coins = cp.intvar(0, 100, shape=len(coins))
    pay.append(pay_coins)

    # The sum of coin values must equal amount
    model += (cp.sum([pay_coins[i]*coins[i] for i in range(len(coins))]) == amount)

    # For each coin used in paying amount, it must not exceed the total coins available
    for i in range(len(coins)):
        model += (pay_coins[i] <= x[i])

# Objective: minimize total number of coins used
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
