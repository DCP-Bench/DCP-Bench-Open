# Import libraries
from cpmpy import *
import json

# Decision Variables
prices = intvar(1, 711, shape=4, name="prices")  # Prices of the four items in cents

# Model
model = Model()

# Constraint: sum of prices is 711 cents ($7.11)
model += sum(prices) == 711

# Constraint: product of prices is 711000000 (711 * 100^3)
model += (prices[0] * prices[1] * prices[2] * prices[3]) == 711000000

# Solve
model.solve()

# Print solution with sorted prices
solution = {
    "prices": sorted(prices.value().tolist())
}
print(json.dumps(solution))
# End of CPMPy script