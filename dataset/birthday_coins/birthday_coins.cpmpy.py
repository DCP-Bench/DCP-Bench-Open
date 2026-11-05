#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/birthday_coins.py
# Source description: https://matmod.ch/lpl/PDF//math10.pdf

# Import libraries
from cpmpy import *
import json

# Parameters
coin_types = 3
values = [30, 12, 6]  # Values in pence for half-crowns, shillings, and sixpences
total_value = 240 + 5 * 12 + 6  # Total value in pence
total_coins = 15  # Total number of coins

# Decision variables
coins = intvar(0, 15, shape=coin_types, name="coins")
half_crowns = coins[0]

# Model
model = Model([
    sum(values[i] * coins[i] for i in range(coin_types)) == total_value,
    sum(coins) == total_coins
])

# Solve the model
model.solve()

# Print the solution
solution = {
    "half_crowns": half_crowns.value(),
}
print(json.dumps(solution))
# End of CPMPy script
