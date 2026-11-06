#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/set_game.ipynb
# Description: https://en.wikipedia.org/wiki/Set_(card_game)

# Data
# Constants
numbers = ONE, TWO, THREE = 1, 2, 3
colors = RED, PURPLE, GREEN = 1, 2, 3
shapes = DIAMOND, RECT, ELLIPSE = 1, 2, 3
fills = FULL, EMPTY, STRIPED = 1, 2, 3

# Make the card deck
cards_data = [  # Each card is represented as a list of [number, fill, color, shape]
    [ONE, EMPTY, GREEN, DIAMOND],
    [TWO, STRIPED, RED, RECT],
    [THREE, STRIPED, GREEN, DIAMOND],
    [THREE, FULL, RED, DIAMOND],
    [ONE, STRIPED, GREEN, DIAMOND],
    [ONE, EMPTY, RED, DIAMOND],
    [TWO, FULL, PURPLE, DIAMOND],
    [THREE, FULL, PURPLE, ELLIPSE],
    [THREE, FULL, GREEN, RECT],
    [ONE, FULL, PURPLE, DIAMOND],
    [ONE, STRIPED, PURPLE, DIAMOND],
    [ONE, FULL, GREEN, RECT]
]
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
cards = cpm_array(cards_data)
given_numbers, given_fills, given_colors, given_shapes = cards[:, 0], cards[:, 1], cards[:, 2], cards[:, 3]

# decision variables
n_cards = len(cards)
winning_cards = intvar(0, n_cards - 1, shape=3, name="winning")  # indices of the winning cards
c1, c2, c3 = winning_cards

# constraints
model = Model()
model += AllDifferent(winning_cards)

# numbers must be all equal or all different
winning_nbs = [given_numbers[c1], given_numbers[c2], given_numbers[c3]]
model += AllEqual(winning_nbs) | AllDifferent(winning_nbs)

# filling pattern must be all equal or all different
winning_fills = [given_fills[c1], given_fills[c2], given_fills[c3]]
model += AllEqual(winning_fills) | AllDifferent(winning_fills)

# colors must be all equal or all different
winning_colors = [given_colors[c1], given_colors[c2], given_colors[c3]]
model += AllEqual(winning_colors) | AllDifferent(winning_colors)

# shapes must be all equal or all different
winning_shapes = [given_shapes[c1], given_shapes[c2], given_shapes[c3]]
model += AllEqual(winning_shapes) | AllDifferent(winning_shapes)

# Solve
model.solve()

# Print
solution = {"winning_cards": winning_cards.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
