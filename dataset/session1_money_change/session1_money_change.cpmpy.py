#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/money_change.mzn

"""
Alice has to give Bob some change. She has different types of coins of different values and she has a certain number of coins of each value available. How can the change be
composed with the available coins minimizing the number of coins used?

Print the number of coins of each type to give to Bob (coin_counts) as a list of integers.
"""

# Data
amount = 199  # amount of money to give to Bob
types_of_coins = [1, 2, 5, 10, 25, 50]  # value of each type of coin
available_coins = [20, 10, 15, 8, 4, 2]  # number of available coins of each type
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(types_of_coins)  # number of types of coins

# Decision Variables
coin_counts = intvar(0, max(available_coins), shape=n)  # number of coins of each type to give to Bob

# Constraints
model = Model()

# The sum of the coins given to Bob must be equal to the amount of money to give him
model += sum(coin_counts[i] * types_of_coins[i] for i in range(n)) == amount

# The number of each type of coin given to Bob must not exceed the available coins
for i in range(n):
    model += coin_counts[i] <= available_coins[i]

# Objective: Minimize the total number of coins given to Bob
model.minimize(sum(coin_counts))

# Solve
model.solve()

# Print the solution
solution = {"coin_counts": coin_counts.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script