#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/farmer_and_cows.mzn

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