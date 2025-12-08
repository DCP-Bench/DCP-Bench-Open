#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/football.py

"""
Statistics show that, in the Premiership, there is a strong
correlation between the value of a team's players and their final
position in that league - so you want to spend as much money as you
can. The chairman gives you an upper limit of GBP 30 million - so you
want your purchases to add up to as close to that figure as possible
(without going over).

Here are the groups of players available, their price (in GBP
millions) and the numbers of each type you are obliged to buy:

Goalkeepers (must buy 1 exactly):
g1: 0.73
g2: 1.28
g3: 3.88

Defenders (must buy 2 or more):
d1: 0.92
d2: 1.31
d3: 1.62
d4: 2.41
d5: 2.79
d6: 3.28
d7: 3.91
d8: 4.57

Midfielders (must buy 3 or more):
m1: 1.8
m2: 2.63
m3: 3.17
m4: 3.769
m5: 4.14
m6: 4.75
m7: 5.38
m8: 5.93
m9: 6.78
m10: 7.13

Strikers (must buy 2 or more):
s1: 4.46
s2: 6.47
s3: 7.78
s4: 8.39
s5: 9.5

Also, you must buy at least eleven players in total.

Print out the total price of the players you have selected (z) in GBP thousands; e.g. if the total is GBP 12,345 million, the output should be 12345.
"""

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
