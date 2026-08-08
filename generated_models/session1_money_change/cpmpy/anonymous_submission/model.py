# Import libraries
from cpmpy import *
import json

# Parameters
coin_values = [1, 2, 5, 10, 25, 50]  # Available coin denominations
coin_available = [20, 10, 15, 8, 4, 2]  # Available quantity of each coin type
target = 199  # Target amount in euros

# Decision Variables
coin_counts = intvar(0, max(coin_available), shape=len(coin_values), name="coin_counts")  # Number of each coin type to use

# Model
model = Model()

# Constraint: sum of coins must equal target amount
model += sum(coin_counts[i] * coin_values[i] for i in range(len(coin_values))) == target

# Constraint: can't use more coins than available
model += [coin_counts[i] <= coin_available[i] for i in range(len(coin_values))]

# Objective: minimize total number of coins used
model.minimize(sum(coin_counts))

# Solve
model.solve()

# Print solution
solution = {
    "coin_counts": coin_counts.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script