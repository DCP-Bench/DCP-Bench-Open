#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/calvin_puzzle.py
# Source description: From 'An Exercise for the Mind: A 10 by 10 Math Puzzle: A Pattern Recognition Game: Meditation on an Open Maze', http://www.chycho.com/?q=Puzzle

"""
The Purpose of the Game

To take an n by n grid, representing n^2 squares, and completely fill every square
based on two types of movements.

Movement Type I)  If the next number in the sequence is going to be placed vertically
or horizontally, then it must be placed exactly three squares away from the previous
number (there must be a two square gap between the numbers).

Movement Type II) If the next number in the sequence is going to be placed diagonally,
then it must be placed exactly two squares away from the previous number (there must
be a one square gap between the numbers).

Print the completed grid (x) as a list of lists of integers.
"""

# Data
n = 5
# End of data

# Import libraries
from cpmpy import *
import json

# Decision variables
x = intvar(1, n * n, shape=(n, n), name="x")

x_flat = [x[i, j] for i in range(n) for j in range(n)]

model = Model(AllDifferent(x_flat))
# <SYMMETRY_BREAKING_CONSTRAINT_START>
# model += (x[0, 0] == 1)
# <SYMMETRY_BREAKING_CONSTRAINT_END>

for k in range(1, n * n):
    i = intvar(0, n - 1, name=f"i_{k}")
    j = intvar(0, n - 1, name=f"j_{k}")
    a = intvar(-3, 3, name=f"a_{k}")
    b = intvar(-3, 3, name=f"b_{k}")

    # Ensure that we are in the square
    model += [i + a >= 0, i + a <= n - 1, j + b >= 0, j + b <= n - 1]

    # model += [a != -1, a != 1, b != -1, b != 1]

    model += [((abs(a) == 3) & (b == 0)) |
              ((abs(b) == 3) & (a == 0)) |
              ((abs(a) == 2) & (abs(b) == 2))
              ]

    # Valid moved
    # model += [ ((a == 3) & (b == 0))  |
    #            ((a == -3) & (b == 0)) |

    #            ((b == 3) & (a == 0))  |
    #            ((b == -3) & (a == 0)) |

    #            ((a == 2) & (b == 2))  |
    #            ((a == 2) & (b == -2)) |
    #            ((a == -2) & (b == 2)) |
    #            ((a == -2) & (b == -2))
    #         ]

    # 1) First: fix this k, i.e.
    model += [k == Element(x_flat, (i * n) + j)]

    # 2) Then, find the position of the next value, i.e.
    model += [(k + 1) == Element(x_flat, ((i + a) * n) + (j + b))]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
