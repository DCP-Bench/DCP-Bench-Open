#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob015_shur_lemma.py
# Source description and problem instances: https://www.csplib.org/Problems/prob015/

"""
The problem is to put \( n \) balls labelled \( 1, \ldots, n \) into 3 boxes so that for any triple of balls
\( (x, y, z) \) with \( x + y = z \), not all are in the same box. This has a solution iff \( n < 14 \). The problem can
be formulated as a 0-1 problem using the variables \( M_{ij} \) for \( i \in \{1, \ldots, n\}, j \in \{1, 2, 3\} \) with
\( M_{ij} \) true if ball \( i \) is in box \( j \). The constraints are that a ball must be in exactly one box,
\( M_{i1} + M_{i2} + M_{i3} = 1 \) for all \( i \in \{1, \ldots, n\} \). And for each \( x + y = z \) and
\( j \in \{1, 2, 3\} \), not \( (M_{xj} \land M_{yj} \land M_{zj}) \). This converts to,
\( (1 - M_{xj}) + (1 - M_{yj}) + (1 - M_{zj}) \geq 1 \) or, \( M_{xj} + M_{yj} + M_{zj} \leq 2 \).

Print the assignment of balls to boxes (balls) as a list of n integers from 1 to 3.
"""

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
