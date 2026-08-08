# Import libraries
from cpmpy import *
import json

# Parameters
denominations = [1, 2, 5, 10, 20, 50]  # Available coin denominations in cents
max_amount = 99  # Maximum amount to pay (99 cents = less than 1 Euro)
max_coins = 99  # Upper bound on number of coins per denomination

# Decision Variables
x = intvar(0, max_coins, shape=len(denominations), name="x")  # Number of each coin type

# Model
model = Model()

# For each amount from 1 to 99 cents, ensure it can be paid exactly
for amount in range(1, max_amount + 1):
    # Variables to represent the coins used for this specific amount
    y = intvar(0, max_coins, shape=len(denominations), name=f"y_{amount}")
    
    # Constraint: the sum of coins*y equals the amount
    model += sum(y[i] * denominations[i] for i in range(len(denominations))) == amount
    
    # Constraint: we can't use more coins than we have available
    model += [y[i] <= x[i] for i in range(len(denominations))]

# Objective: minimize total number of coins
model.minimize(sum(x))

# Solve
model.solve()

# Print solution
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script