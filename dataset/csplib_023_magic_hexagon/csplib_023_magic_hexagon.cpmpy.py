#!/usr/bin/python3
# Category: csplib
# Source: https://www.csplib.org/Problems/prob023/

"""
A magic hexagon problem involves arranging the numbers 1 to 19 in a hexagonal pattern
such that the sum of the numbers in each of the 15 lines (rows and diagonals) is
equal to a magic constant, which is 38.

The hexagonal grid is structured as follows:
      A, B, C
     D, E, F, G
    H, I, J, K, L
     M, N, O, P
      Q, R, S

The goal is to find an assignment of numbers to the variables A through S that
satisfies all the sum constraints.

Print the solution (LD) as a single list of 19 integers corresponding to the
variables [A, B, ..., S].
"""

# Data
NUM_CELLS = 19  # Number of cells in the hexagon, 3 + 4 + 5 + 4 + 3
MAGIC_SUM = 38  # The magic constant for the hexagon
# End of data

import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# Create 19 integer variables, one for each cell in the hexagon, with values from 1 to 19.
LD = cp.intvar(1, NUM_CELLS, shape=NUM_CELLS, name="LD")

# Unpack the array into individual variables for readability, corresponding to the grid.
a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s = LD

# Constraints
# 1. All numbers from 1 to 19 must be used exactly once.
model += cp.AllDifferent(LD)

# 2. The sum of each of the 15 lines must equal the MAGIC_SUM.
# Rows (horizontal)
model += (cp.sum([a, b, c]) == MAGIC_SUM)
model += (cp.sum([d, e, f, g]) == MAGIC_SUM)
model += (cp.sum([h, i, j, k, l]) == MAGIC_SUM)
model += (cp.sum([m, n, o, p]) == MAGIC_SUM)
model += (cp.sum([q, r, s]) == MAGIC_SUM)

# Diagonals (top-left to bottom-right)
model += (cp.sum([a, d, h]) == MAGIC_SUM)
model += (cp.sum([b, e, i, m]) == MAGIC_SUM)
model += (cp.sum([c, f, j, n, q]) == MAGIC_SUM)
model += (cp.sum([g, k, o, r]) == MAGIC_SUM)
model += (cp.sum([l, p, s]) == MAGIC_SUM)

# Diagonals (top-right to bottom-left)
model += (cp.sum([c, g, l]) == MAGIC_SUM)
model += (cp.sum([b, f, k, p]) == MAGIC_SUM)
model += (cp.sum([a, e, j, o, s]) == MAGIC_SUM)
model += (cp.sum([d, i, n, r]) == MAGIC_SUM)
model += (cp.sum([h, m, q]) == MAGIC_SUM)

# This is a satisfaction problem, so there is no objective function.

# Solve and print
model.solve()
solution = {
    "LD": LD.value().tolist()
}
print(json.dumps(solution))
# End of CPMpy script