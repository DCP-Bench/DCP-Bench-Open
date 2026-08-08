from cpmpy import *
import json

# Input data
coin_values = [1, 2, 5, 10, 25, 50]  # Values of the coins
available_coins = [20, 10, 15, 8, 4, 2]  # Available number of coins for each type
target_change = 199  # Target change to give

# Decision variables
# coin_counts[i] is the number of coins of type i to use
coin_counts = intvar(0, 100, shape=len(coin_values), name="coin_counts")

# Model
model = Model()

# Objective: minimize the total number of coins used
model.minimize(sum(coin_counts))

# Constraint: total value of coins must equal the target change
model += [sum(coin_values[i] * coin_counts[i] for i in range(len(coin_values))) == target_change]

# Constraint: cannot use more coins than available for each type
for i in range(len(coin_values)):
    model += [coin_counts[i] <= available_coins[i]]

# Solve the model
model.solve()

# Print the solution
solution = {"coin_counts": coin_counts.value().tolist()}
print(json.dumps(solution))