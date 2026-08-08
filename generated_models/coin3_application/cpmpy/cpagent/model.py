import cpmpy as cp
import numpy as np
import json

# Problem: Find minimum number of coins to pay exactly any amount < 1 Euro (100 cents)
# Denominations: 1, 2, 5, 10, 20, 50 cents
# Objective: Minimize total number of coins

denominations = [1, 2, 5, 10, 20, 50]
n_denoms = len(denominations)
max_amount = 99  # Any amount smaller than 100 cents (1 Euro)

model = cp.Model()

# Decision variables: x[i] = number of coins of denomination denominations[i]
# Upper bound: worst case is paying 99 cents with 1-cent coins = 99 coins
max_coins_per_denom = max_amount
x = cp.intvar(0, max_coins_per_denom, shape=n_denoms, name="x")

# Constraint: Must be able to pay exactly any amount from 1 to 99 cents
# For each amount, we need auxiliary variables representing how many coins of each type to use
for amount in range(1, max_amount + 1):
    # For this amount, create variables for how many coins of each denomination to use
    coins_used = cp.intvar(0, max_coins_per_denom, shape=n_denoms, name=f"coins_used_{amount}")
    
    # The coins used for this amount must sum to the amount
    model += cp.sum([coins_used[i] * denominations[i] for i in range(n_denoms)]) == amount
    
    # The coins used cannot exceed the coins we have
    for i in range(n_denoms):
        model += coins_used[i] <= x[i]

# Objective: Minimize total number of coins
total_coins = cp.sum(x)
model.minimize(total_coins)

# Solve the model
if model.solve():
    # Extract solution
    solution_values = x.value()
    solution = {"x": solution_values.tolist()}
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))