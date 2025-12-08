#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/mario.py

"""
Mario needs to collect as much gold as possible by visiting different houses. He starts at Mario's house and ends at
Luigi's house. Each house has a certain amount of gold and the travel between houses consumes fuel. Mario has a
limited amount of fuel, and he needs to plan his route to maximize the gold collected without exceeding the fuel limit.

Print the succeeding houses for each house (s) as a list of integers, s[i] is the house succeeding to the ith house, s[i]=i if not part of the route.
For luigi's house, the succeeding house should be Mario's house.
"""

# Data
nHouses = 15
marioHouse = 0  # 0-indexed
luigiHouse = 1  # 0-indexed
fuelLimit = 600
# fuel consumption between houses, conso[i][j] = fuel from i to j
arc_fuel = [
    [0, 221, 274, 808, 13, 677, 670, 921, 943, 969, 13, 18, 217, 86, 322],  # Mario's house
    [0, 0, 702, 83, 813, 679, 906, 246, 335, 529, 719, 528, 451, 242, 712],  # Luigi's house
    [274, 702, 0, 127, 110, 72, 835, 5, 161, 430, 686, 664, 799, 523, 73],
    [808, 83, 127, 0, 717, 80, 31, 71, 683, 668, 248, 826, 916, 467, 753],
    [13, 813, 110, 717, 0, 951, 593, 579, 706, 579, 101, 551, 280, 414, 294],
    [677, 679, 72, 80, 951, 0, 262, 12, 138, 222, 146, 571, 907, 225, 938],
    [670, 906, 835, 31, 593, 262, 0, 189, 558, 27, 287, 977, 226, 454, 501],
    [921, 246, 5, 71, 579, 12, 189, 0, 504, 221, 483, 226, 38, 314, 118],
    [943, 335, 161, 683, 706, 138, 558, 504, 0, 949, 393, 721, 267, 167, 420],
    [969, 529, 430, 668, 579, 222, 27, 221, 949, 0, 757, 747, 980, 589, 528],
    [13, 719, 686, 248, 101, 146, 287, 483, 393, 757, 0, 633, 334, 492, 859],
    [18, 528, 664, 826, 551, 571, 977, 226, 721, 747, 633, 0, 33, 981, 375],
    [217, 451, 799, 916, 280, 907, 226, 38, 267, 980, 334, 33, 0, 824, 491],
    [86, 242, 523, 467, 414, 225, 454, 314, 167, 589, 492, 981, 824, 0, 143],
    [322, 712, 73, 753, 294, 938, 501, 118, 420, 528, 859, 375, 491, 143, 0]
]
goldInHouse = [0, 0, 40, 67, 89, 50, 6, 19, 47, 68, 94, 86, 34, 14, 14]
# End of data

# Import libraries
from cpmpy import *
import json

arc_fuel = cpm_array(arc_fuel)  # needed to do arc_fuel[var1] == var2

# s[i] is the house succeeding to the ith house (s[i]=i if not part of the route)
s = intvar(0, nHouses - 1, shape=nHouses, name="s")

model = Model()

# 1. All houses must be assigned a successor, including Mario's and Luigi's houses.
model += AllDifferent(s)

# 2. Auxiliary variables for the rank of each house in the tour
order = intvar(1, nHouses, shape=nHouses, name="order")

# 3. All ranks must be unique.
model += AllDifferent(order)

# 4. The tour starts at marioHouse, which is assigned rank 1.
model += order[marioHouse] == 1

# 5. The path ends at luigiHouse, which must loop back to marioHouse.
model += s[luigiHouse] == marioHouse

# 6. Enforce rank progression and segregate non-tour nodes.
for i in range(nHouses):
    # Part A: Rank Progression
    # For a node 'i' on the tour, its successor's rank must be exactly one greater.
    # We exclude the final arc from luigiHouse back to marioHouse, as the rank resets there.
    model += ((s[i] != i) & (s[i] != marioHouse)).implies(order[s[i]] == order[i] + 1)

    # Part B: Rank Segregation
    # Any node 'i' is either on the tour, OR its rank must be higher than the rank of the last node on the tour (luigiHouse).
    # This ensures nodes not on the main tour do not form their own ranked subtours.
    model += (s[i] != i) | (order[luigiHouse] < order[i])

# consumption, knowing that always conso[i,i]=0
node_fuel = [arc_fuel[i, s[i]] for i in range(nHouses)]
model += sum(node_fuel) < fuelLimit

# amount of gold earned, only for stops visited, s[i] != i
gold = sum((s != range(nHouses)) * goldInHouse)
model.maximize(gold)

# Solve
model.solve()

# Print
solution = {"s": s.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
