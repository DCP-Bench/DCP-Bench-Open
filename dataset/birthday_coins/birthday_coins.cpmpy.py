#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/birthday_coins.py
# Source description: https://matmod.ch/lpl/PDF//math10.pdf

"""
Tommy was given 15 coins for his birthday (half-crowns, shillings and sixpence).
When he added it up, he found that he had £1. 5s. 6d (one pound 5 shillings and 6 pences, see
below). How many half-crowns was he given?

(This puzzle involve coins from the old British currency. A pound is 20 shillings and a
shilling is 12 pence (hence, a pound is 20 ⋅ 12 = 240 pence). A half-sovereign is 10 shillings,
a crown is 5 shillings, a double-florin is four shillings, a half-crown is 2 shillings and sixpence
(hence, a half-crown is 2 ⋅ 12 + 6 = 30 pence), a florin is 2 shillings. £3. 2s. 6d. means three
pounds, two shillings and six pence.).

Print the number of half-crowns he was given (half_crowns).
"""

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
