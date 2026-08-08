from cpmpy import *
import json

# Denominations of coins in cents
denominations = [1, 2, 5, 10, 20, 50]

# Number of different coin denominations
num_coins = len(denominations)

# Decision variables: number of each type of coin used
x = intvar(0, 100, shape=num_coins, name="x")

# Model
model = Model()

# Objective: minimize the total number of coins
model.minimize(sum(x))

# Constraints: For each amount from 1 to 99 cents, we must be able to form it using the coins
for amount in range(1, 100):
    # Binary variables to indicate if a coin is used in forming the amount
    use_coin = boolvar(shape=num_coins, name=f"use_coin_{amount}")
    
    # The total value of the selected coins must equal the amount
    model += [sum(denominations[i] * use_coin[i] for i in range(num_coins)) == amount]
    
    # The number of coins used for this amount must not exceed the available number of coins
    for i in range(num_coins):
        model += [use_coin[i] <= x[i]]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))