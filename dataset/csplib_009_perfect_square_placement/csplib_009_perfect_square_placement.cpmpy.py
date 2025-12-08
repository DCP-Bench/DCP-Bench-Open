#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob009_perfect_squares.py
# Source description: https://www.csplib.org/Problems/prob009/
# Problem instances: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob009_perfect_squares.json

"""
The perfect square placement problem (also called the squared square problem) is to pack a set of squares with given
integer sizes into a bigger square in such a way that no squares overlap each other and all square borders are
parallel to the border of the big square. The sum of the square surfaces is equal to the surface of the packing square, so that there is no spare capacity. A simple
perfect square placement problem is a perfect square placement problem in which no subset of the squares (greater than
one) are placed in a rectangle.

Print the coordinates of the squares (x_coords, y_coords) as lists of integers - starting from 0.
"""

# Data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *
from cpmpy.expressions.utils import all_pairs

def perfect_squares(base, sides):
    model = Model()
    sides = np.array(sides)

    squares = range(len(sides))

    # Ensure that the squares cover the base exactly
    assert np.square(sides).sum() == base ** 2, "Squares do not cover the base exactly!"

    # Variables
    x_coords = intvar(0, base, shape=len(squares), name="x_coords")
    y_coords = intvar(0, base, shape=len(squares), name="y_coords")

    # Squares must be in bounds of big square
    model += x_coords + sides <= base
    model += y_coords + sides <= base

    # No overlap between squares
    for a, b in all_pairs(squares):
        model += (
            (x_coords[a] + sides[a] <= x_coords[b]) |
            (x_coords[b] + sides[b] <= x_coords[a]) |
            (y_coords[a] + sides[a] <= y_coords[b]) |
            (y_coords[b] + sides[b] <= y_coords[a])
        )

    return model, (x_coords, y_coords)

# Example usage
model, (x_coords, y_coords) = perfect_squares(base, sides)

# Solve
model.solve()

# Print
solution = {
    "x_coords": x_coords.value().tolist(),
    "y_coords": y_coords.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
