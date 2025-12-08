#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/kenken2.py

"""
KenKen or KEN-KEN is a style of arithmetic and logical puzzle sharing
several characteristics with sudoku. The name comes from Japanese and
is translated as 'square wisdom' or 'cleverness squared'.

The objective is to fill the grid in with the digits 1 through 6 such that:

  * Each row contains exactly one of each digit
  * Each column contains exactly one of each digit
  * Each bold-outlined group of cells is a cage containing digits which
    achieve the specified result using the specified mathematical operation:
      addition (+),
      subtraction (-),
      multiplication (x),
      and division (/).
      (Unlike in Killer sudoku, digits may repeat within a group.)

More complex KenKen problems are formed using the principles described
above but omitting the symbols +, -, x and /, thus leaving them as
yet another unknown to be determined.

Print the solved grid (x) as a list of lists of integers ranging from 1 to 6.
"""

# Data
# size of matrix
n = 6

# For a better view of the problem, see
#  http://en.wikipedia.org/wiki/File:KenKenProblem.svg

# hints
#    [sum, [segments]]
# Note: 1-based
problem = [[11, [[1, 1], [2, 1]]], [2, [[1, 2], [1, 3]]],
           [20, [[1, 4], [2, 4]]], [6, [[1, 5], [1, 6], [2, 6], [3, 6]]],
           [3, [[2, 2], [2, 3]]], [3, [[2, 5], [3, 5]]],
           [240, [[3, 1], [3, 2], [4, 1], [4, 2]]], [6, [[3, 3], [3, 4]]],
           [6, [[4, 3], [5, 3]]], [7, [[4, 4], [5, 4], [5, 5]]],
           [30, [[4, 5], [4, 6]]], [6, [[5, 1], [5, 2]]],
           [9, [[5, 6], [6, 6]]], [8, [[6, 1], [6, 2], [6, 3]]],
           [2, [[6, 4], [6, 5]]]]

num_p = len(problem)
# End of data

from cpmpy import *
import json
from functools import reduce


def prod1(_x):
    """
    prod1(x)

    return the product of the values in x.
    """
    return reduce(lambda _a, _b: _a * _b, _x)


model = Model()

x = intvar(1, n, shape=(n, n), name="x")

# all rows and columns must be unique
model += [AllDifferent(row) for row in x]
model += [AllDifferent(col) for col in x.transpose()]

# calculate the segments
for (res, segment) in problem:
    if len(segment) == 2:

        # for two operands there may be
        # a lot of variants
        c00, c01 = segment[0]
        c10, c11 = segment[1]
        a = x[c00 - 1, c01 - 1]
        b = x[c10 - 1, c11 - 1]
        model += [(a + b == res) |
                  (a * b == res) |
                  (a * res == b) |
                  (b * res == a) |
                  (a - b == res) |
                  (b - a == res)
                  ]

    else:
        # res is either sum or product of the segment
        xx = [x[i[0] - 1, i[1] - 1] for i in segment]
        model += [(sum(xx) == res) |
                  # (reduce(lambda a, b: a * b, xx) == res)
                  # (prod(xx,res)
                  (prod1(xx) == res)
                  ]

model.solve()

# Output
solution = {
    'x': x.value().tolist()
}
print(json.dumps(solution, indent=4))
# End of CPMPy script
