#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/farmer_and_cows.mzn

"""
A farmer has a number of cows, with each cow numbered from 1 up to the total number of cows. Each cow gives a quantity of milk equal to its number. The farmer has a number of sons and wants to distribute his cows to them according to a given distribution. The total quantity of milk produced should be the same for each son. How can he distribute the cows?

Print the assignment of cows to sons (cow_assignments), as a list of integers, where the index of the list corresponds to the cow and the value to the son, e.g., [0, 1, 0, 2] means that cow 1 goes to son 0, cow 2 to son 1, cow 3 to son 0, and cow 4 to son 2.
"""

# Data
num_cows = 25
num_sons = 5
cows_per_son = [7, 6, 5, 4, 3]
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
milk_per_cow = list(range(1, num_cows + 1))
total_milk = sum(milk_per_cow)  # Total milk produced by all cows
total_milk_per_son = total_milk // num_sons  # Total milk each son should get

# Decision variables
# Each cow is assigned to a son, represented by an integer from 0 to num_sons-1
cow_assignments = intvar(0, num_sons - 1, shape=num_cows)

# Constraints
model = Model()

# Each son gets a specific number of cows
for son in range(num_sons):
    model += sum(cow_assignments == son) == cows_per_son[son]

# The total milk production for each son is equal
for son in range(num_sons):
    model += sum(milk_per_cow[i] * (cow_assignments[i] == son) for i in range(num_cows)) == total_milk_per_son

# Solve
model.solve()

# Print the solution
solution = {"cow_assignments": cow_assignments.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script