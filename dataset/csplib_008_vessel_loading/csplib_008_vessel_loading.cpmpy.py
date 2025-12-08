#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob008_vessel_loading.py
# Source description: https://www.csplib.org/Problems/prob008/

"""
Supply vessels transport containers from site to site. The deck area is rectangular. Containers are cuboid, and are
laid out in a single layer. All containers are positioned parallel to the sides of the deck. The contents of the
containers determine their class. Certain classes of containers are constrained to be separated by minimum distances
either along the deck or across the deck.

The vessel loading decision problem is to determine whether a given set of containers can be positioned on a given
deck, without overlapping, and without violating any of the separation constraints.

Print the positions of the containers (left, right, top, bottom), as lists of integers - starting from 0.
"""

# Data
deck_width = 5  # Width of the deck
deck_length = 5  # Length of the deck
n_containers = 3  # Number of containers
width = [5, 2, 3]  # Widths of containers
length = [1, 4, 4]  # Lengths of containers
classes = [1, 1, 1]  # Classes of containers
separation = [  # Separation constraints between classes
    [0, 0],
    [0, 0]
]
# End of data

# Import libraries
from cpmpy import *
import json
from cpmpy.expressions.utils import all_pairs

# Create the model
model = Model()

# Declare variables
left = intvar(0, deck_width, shape=n_containers, name="left")
right = intvar(0, deck_width, shape=n_containers, name="right")
top = intvar(0, deck_length, shape=n_containers, name="top")
bottom = intvar(0, deck_length, shape=n_containers, name="bottom")

# Set shape of containers
for i in range(n_containers):
    model += ((right[i] - left[i] == width[i]) & (top[i] - bottom[i] == length[i])) | \
             ((right[i] - left[i] == length[i]) & (top[i] - bottom[i] == width[i]))

# No overlap between containers
for x, y in all_pairs(range(n_containers)):
    c1, c2 = classes[x], classes[y]
    sep = separation[c1 - 1][c2 - 1]
    model += (
            (right[x] + sep <= left[y]) |  # x at least sep left of y or
            (left[x] >= right[y] + sep) |  # x at least sep right of y or
            (top[x] + sep <= bottom[y]) |  # x at least sep under y or
            (bottom[x] >= top[y] + sep)  # x at least sep above y
    )

# Solve
model.solve()

# Print
solution = {
    "left": left.value().tolist(),
    "right": right.value().tolist(),
    "top": top.value().tolist(),
    "bottom": bottom.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
