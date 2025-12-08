#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/packing_rectangles.ipynb
# Source Description: https://github.com/Alexander-Schiendorfer/cp-examples/tree/main/packing

"""
The rectangular packing problem involves placing a set of rectangular items into a larger rectangular area such that
no items overlap and all items are within the boundaries of the larger area. The objective is to minimize the total
area of the larger rectangle required to pack all the items.

Given the widths and heights of the items, determine their positions within the larger rectangle while ensuring no
overlap and minimizing the total area.

Print the positions of the items (pos_x, pos_y) starting from 0, and the dimensions of the larger rectangle (total_x, total_y).
"""

# Data
widths = [3, 4, 2, 1]  # Widths of the items
heights = [2, 3, 1, 4]  # Heights of the items
# End of data

# Import libraries
from cpmpy import *
import json
from cpmpy.expressions.utils import all_pairs


def model_packing_rectangular(widths, heights):
    # Number of different items
    n = len(widths)

    # max dimensions of the whole area
    area_min_x, area_max_x = max(widths), sum(widths)
    area_min_y, area_max_y = max(heights), sum(heights)

    # Decision variables
    pos_x = intvar(0, area_max_x, shape=n)
    pos_y = intvar(0, area_max_y, shape=n)

    total_x = intvar(area_min_x, area_max_x)
    total_y = intvar(area_min_y, area_max_y)

    m = Model()

    ## Necessary constraints
    # Every item has to be within the overall area
    m += [pos_x + widths <= total_x,
          pos_y + heights <= total_y]

    # No-overlap: every item has to be fully above, below or next to every other item
    for i, j in all_pairs(range(n)):
        m += ((pos_x[i] + widths[i] <= pos_x[j]) |
              (pos_x[j] + widths[j] <= pos_x[i]) |
              (pos_y[i] + heights[i] <= pos_y[j]) |
              (pos_y[j] + heights[j] <= pos_y[i]))

    # Minimize wrt the overall area
    m.minimize(total_x * total_y)

    ## Optional constraints
    # The needed space needs to be wider than taller
    # m += (total_x > total_y),

    # The needed space has to have a width larger than 10
    # m += (total_x >= 10),

    # The needed space has to have a height larger than 10
    # m += (total_y >= 10)

    return m, (pos_x, pos_y, total_x, total_y)


# Example usage
model, (pos_x, pos_y, total_x, total_y) = model_packing_rectangular(widths, heights)
model.solve()

# Print
solution = {
    "pos_x": pos_x.value().tolist(),
    "pos_y": pos_y.value().tolist(),
    "total_x": total_x.value(),
    "total_y": total_y.value()
}
print(json.dumps(solution))
# End of CPMPy script
