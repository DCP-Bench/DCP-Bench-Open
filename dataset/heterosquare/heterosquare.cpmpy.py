#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/heterosquare.py

"""
A heterosquare of order n is a n*n square whose elements are distinct integers from
1 to n^2 such that the sums of the rows, columns and diagonals are all different.
Here is an example of heterosquare of order 3

           19

1  2  3    6
8  9  4    21
7  6  5    18

16 17 12   15  (Sums)

Print a heterosquare (x) of a given order as a list of lists of integers.
"""

# Data
n = 5  # order
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json
import math

model = Model()

# variables
x = intvar(1, n * n, shape=(n, n), name="x")

row_sums = intvar(1, n ** 3, shape=n, name="row_sums")
col_sums = intvar(1, n ** 3, shape=n, name="col_sums")

diag1 = intvar(1, n ** 3, name="diag1")
diag2 = intvar(1, n ** 3, name="diag2")

# constraints

# all the entries in the matrix should be different
model += (AllDifferent(x))

# and all sums should be different
all_sum_vars = []
all_sum_vars.extend(row_sums)
all_sum_vars.extend(col_sums)
all_sum_vars.append(diag1)
all_sum_vars.append(diag2)
model += AllDifferent(all_sum_vars)

# calculate rows sums
for i in range(n):
    model += (row_sums[i] == sum(x[i, :]))

# calculate column sums
for j in range(n):
    model += (col_sums[j] == sum(x[:, j]))

# diag1 sums
model += (sum([x[i, i] for i in range(n)]) == diag1)

# diag2 sums
model += (sum([x[i, n - i - 1] for i in range(n)]) == diag2)
# Solve
model.solve()

# Output
solution = {
    "x": x.value().tolist(),
}
print(json.dumps(solution))
# End of CPMPy script