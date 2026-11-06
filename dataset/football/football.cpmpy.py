#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/football.py

# Import libraries
from cpmpy import *
import numpy as np
import json

# Parameters

# Multiply money values with 1000
budget = 30000  # GBP thousands
num_players = [3, 8, 10, 5]
num_types = len(num_players)
max_num_players = max(num_players)
# min/max of players to buy
min_max = [[1, 1],
           [2, max_num_players],
           [3, max_num_players],
           [2, max_num_players]]

# cost matrix (0 means no player)
costs = [[ 730, 1280, 3880,    0,    0,    0,    0,    0,    0,    0],
         [ 920, 1310, 1620, 2410, 2790, 3280, 3910, 4570,    0,    0],
         [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
         [4460, 6470, 7780, 8390, 9500,    0,    0,    0,    0,    0]]

# the decision variables, i.e. whether we should buy a player or not.
x = boolvar(shape=(num_types, max_num_players), name="x")

# the total cost of the choosen players
z = intvar(0, budget, name="z")  # total cost in GBP thousands
num_player_chosen = intvar(0, sum(num_players), name="num_player_chosen")

model = Model(
    [z == sum([x[i, j] * costs[i][j] for i in range(num_types) for j in range(max_num_players) if costs[i][j] > 0]),
     num_player_chosen == x.sum()
     ])

# minimum/maximum of players to buy
for i in range(num_types):
    s = intvar(min_max[i][0], min_max[i][1], name=f"s[{i}]")
    model += [s == sum([x[i, j] == 1 for j in range(max_num_players) if costs[i][j] > 0])]

# consider only the "real" players, i.e. not the "0" filled
for i in range(num_types):
    for j in range(max_num_players):
        model += [(costs[i][j] == 0) <= (x[i, j] == 0)]

model += [z <= budget]
model += [num_player_chosen >= 11]

model.maximize(z)
model.solve()

solution = {"z": z.value()}
print(json.dumps(solution))
# End of CPMPy script
