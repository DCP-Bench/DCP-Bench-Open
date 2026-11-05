#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob015_shur_lemma.py
# Source description and problem instances: https://www.csplib.org/Problems/prob015/

# Data
n = 13  # Number of balls
c = 3  # Number of boxes
# End of data

# Import libraries
import json
from cpmpy import *


def shur_lemma(n, c):
    # balls[i] = j iff ball i is in box j
    balls = intvar(1, c, shape=n, name="balls")

    model = Model()

    # Ensure each triple (x, y, z) with x + y = z are not in the same box
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z <= n:
                model += (balls[x - 1] != balls[y - 1]) | \
                         (balls[x - 1] != balls[z - 1]) | \
                         (balls[y - 1] != balls[z - 1])

    return model, (balls,)


# Example usage
model, (balls,) = shur_lemma(n, c)
model.solve()

# Print
solution = {"balls": balls.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
