#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/set_game.ipynb
# Description: https://en.wikipedia.org/wiki/Set_(card_game)

"""
Set (stylized as SET or SET!) is a real-time card game designed by Marsha Falco in 1974 and published by Set
Enterprises in 1991. The deck consists of 81 unique cards that vary in four features across three possibilities for
each kind of feature: number of shapes (one, two, or three), shape (diamond, squiggle, oval), shading (solid,
striped, or open), and color (red, green, or purple).[2] Each possible combination of features (e.g. a card with
three striped green diamonds) appears as a card precisely once in the deck.

In the game, certain combinations of three cards are said to make up a "set". For each one of the four categories of
features—color, number, shape, and shading—the three cards must display that feature as either a) all the same,
or b) all different. Put another way: For each feature the three cards must avoid having two cards showing one
version of the feature and the remaining card showing a different version.

For example, 3 solid red diamonds, 2 solid green squiggles, and 1 solid purple oval form a set, because the shadings
of the three cards are all the same, while the numbers, the colors, and the shapes among the three cards are all
different.

For any set, the number of features that are constant (the same on all three cards) and the number of features that
differ (different on all three cards) may break down as: all 4 features differing; or 1 feature being constant and 3
differing; or 2 constant and 2 differing; or 3 constant and 1 differing. (All 4 features being constant would imply
that the three cards in the set are identical, which is impossible since no cards in the Set deck are identical.)

Print the 0-based indices of the winning set of cards (winning_cards).
"""

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
