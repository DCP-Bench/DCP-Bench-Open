#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/subset_sum.mzn

# Data
total_coins_lost = 100
coin_numbers = [16, 17, 23, 24, 39, 40]
# End of data

# Import libraries
from cpmpy import *
import json

# Decision variables
# The number of bags stolen for each type of coins
bags = intvar(0, total_coins_lost, shape=len(coin_numbers))

# Constraints
model = Model()

# The total number of coins lost is equal to the sum of the coins in the stolen bags
model += sum([bags[i] * coin_numbers[i] for i in range(len(coin_numbers))]) == total_coins_lost

# Solve
model.solve()

# Print the solution
solution = {"bags": bags.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script