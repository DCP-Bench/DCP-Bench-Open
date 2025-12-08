#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/building_blocks.py
# Source description: http://brownbuffalo.sourceforge.net/BuildingBlocksClues.html
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Each of a number of alphabet blocks has a single letter of the alphabet on each
of its sides. In all, the blocks contain every letter but
Q and Z. By arranging the blocks in various ways, you can spell all of
the words in a given list. Can you figure out how the letters are arranged
on the blocks?

Print the solution as a list of num_letters numbers representing at which block each letter is placed (dice), between 0 and num_blocks-1.
"""

# Data
num_blocks = 4
num_sides = 6
words_str = [
    "BAKE", "ONYX", "ECHO", "OVAL", "GIRD", "SMUG", "JUMP", "TORN",
    "LUCK", "VINY", "LUSH", "WRAP"
]
alphabet = "ABCDEFGHIJKLMNOPRSTUVWXY"
num_letters = 24
# End of data

# Import libraries
from cpmpy import *
import json
import numpy as np


def count(a, val, c):
    """
    count(a,val,c)

    c is the number of occurrences of val in array a.
    """
    return [c == sum([a[i] == val for i in range(len(a))])]


def global_cardinality_count(a, gcc):
    """
    global_cardinality_count(a,gcc)

    Global cardinality count: Collect the number of occurrences of each value 0..a.ub
    in gcc. The array gcc must be of length 0..ub.
    """
    n = len(a)
    ub = max([a[i].ub for i in range(n)])
    constraints = []
    for i in range(ub + 1):
        constraints += [count(a, i, gcc[i])]

    return constraints

num_words = len(words_str)

letter_map = {letter: i for i, letter in enumerate(alphabet)}
words = [[letter_map[c] for c in w] for w in words_str]

dice = intvar(0, num_blocks - 1, shape=num_letters, name="dice")

model = Model()

# the letters in a word must be on a different die
for word in words:
    model += (AllDifferent([dice[letter] for letter in word]))

# there must be exactly num_sides letters of each die
model += (global_cardinality_count(dice, [num_sides for i in range(num_blocks)]))

# symmetry breaking (first word is placed)
# <SYMMETRY_BREAKING_CONSTRAINT_START>
# model += (dice[0] <= dice[6])
# model += (dice[6] <= dice[12])
# <SYMMETRY_BREAKING_CONSTRAINT_END>

model.solve()

# Print the solution
solution = {"dice": dice.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script