
import cpmpy as cp
import json

# Data
coin_values = [1, 2, 5, 10, 25, 50]
available_coins = [20, 10, 15, 8, 4, 2]
total_change = 199

# Model definition
model = cp.Model()

# Decision Variables: number of coins of each type to give to Bob
coin_counts = cp.intvar(0, available_coins, shape=len(coin_values), name="coin_counts")

# Constraints
# The total value of coins given must be exactly the change amount
model += (cp.sum([coin_counts[i] * coin_values[i] for i in range(len(coin_values))]) == total_change)

# Objective: minimize the total number of coins used
model.minimize(cp.sum(coin_counts))

# Solve and print
if model.solve():
    solution = {'coin_counts': coin_counts.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
