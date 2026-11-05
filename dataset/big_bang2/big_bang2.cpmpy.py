#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/big_bang2.py
# Misc: Model adjusted for clarity

# Import libraries
from cpmpy import *
import json

# Parameters
rock = 0
paper = 1
scissors = 2
lizard = 3
spock = 4

m = 5  # number of dice
n = 6  # number of faces of each die
f = 12  # max face value of dice
edge = [
    [rock, scissors],  # 1: Rock crushes Scissors
    [rock, lizard],  # etc.
    [paper, rock],
    [paper, spock],
    [scissors, paper],
    [scissors, lizard],
    [lizard, paper],
    [lizard, spock],
    [spock, rock],
    [spock, scissors]
]

# Model definition
model = Model()

# Decision Variables
# dice[i][j] = face value of j-th face of i-th die
dice = intvar(1, f, shape=(m, n), name="dice")

# Constraints
for (winner, loser) in edge:
    # The number of pairs where dice[winner][x] > dice[loser][y] has to be greater than half of the total pairs
    model += sum([dice[winner, x] > dice[loser, y] for x in range(n) for y in range(n)]) > (n * n) // 2

# <SYMMETRY_BREAKING_CONSTRAINT_START>
# # Faces of each die are sorted non-decreasing to break symmetry
# for i in range(m):
#     model += Increasing(dice[i])
#    To reduce symmetry, enforce dice to be distinct sets of faces
#    We can enforce all dice to be different (lex order or all different faces)
#    Here, we enforce all dice to be different lexicographically
# for i in range(m-1):
#     model += LexLess(dice[i], dice[i+1])
# <SYMMETRY_BREAKING_CONSTRAINT_END>

# Solve the model
model.solve()

# Print the solution
solution = {"dice": dice.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
