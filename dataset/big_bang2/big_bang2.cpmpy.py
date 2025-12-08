#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/big_bang2.py
# Misc: Model adjusted for clarity

"""
Nontransitive dice: The idea is to create a set of five dice such that the dominance relationships
between the dice is isomorphic to the corresponding relationships in the game
Rock-Paper-Scissors extended by the choices Lizard and Spock.
Each choice beats two other choices and is beaten by two other choices.
In particular, we have the following ten 'beats' relationships

1:  Rock(1) crushes Scissors(3)
2:  Rock(1) crushes Lizard(4)
3:  Paper(2) covers Rock(1)
4:  Paper(2) disproves Spock(5)
5:  Scissors(3) cuts Paper(2)
6:  Scissors(3) decapitate Lizard(4)
7:  Lizard(4) eats Paper(2)
8:  Lizard(4) poisons Spock(5)
9:  Spock(5) vaporizes Rock(1)
10: Spock(5) smashes Scissors(3)

Print the dice (dice) as a list of lists where each sublist is a die.
"""

# Data
rock = 0
paper = 1
scissors = 2
lizard = 3
spock = 4

m = 5  # number of dice
n = 6  # number of faces of each die
f = 2 * n  # max face value of dice
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
# End of data

# Import libraries
from cpmpy import *
import json


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
