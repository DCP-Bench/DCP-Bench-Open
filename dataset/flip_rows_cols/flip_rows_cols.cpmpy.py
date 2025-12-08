#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/einav_puzzle.py
# Source description: http://gcanyon.wordpress.com/2009/10/28/a-programming-puzzle-from-einav/

"""
Given is an array of positive and negative numbers.
You can flip the sign of entire rows and columns, as many of them
as you like. The goal is to make each one of all the rows and columns sum to positive
numbers (or zero), and then to find the solution (there are more than one)
that has the smallest overall sum. So for example, for this array:
   33  30 -10
  -16  19   9
  -17 -12 -14
You could flip the sign for the bottom row to get this array:
  33  30 -10
 -16  19   9
  17  12  14
Now all the rows and columns have positive sums, and the overall total is 108.
But you could instead flip the second and third columns, and the second
row, to get this array:
  33  -30  10
  16   19    9
 -17   12   14
All the rows and columns still total positive, and the overall sum is just
66. So this solution is better (I don't know if it's the best).

Print the signs of rows and columns to minimize the overall sum (row_signs, col_signs), as two lists containing -1/1,
depending on the selected sign for the respective row/column.
"""

# Data
input_matrix = [
    [33, 30, 10, -6, 18, -7, -11, 23, -6],
    [16, -19, 9, -26, -8, -19, -8, -21, -14],
    [17, 12, -14, 31, -30, 13, -13, 19, 16],
    [-6, -11, 1, 17, -12, -4, -7, 14, -21],
    [18, -31, 34, -22, 17, -19, 20, 24, 6],
    [33, -18, 17, -15, 31, -5, 3, 27, -3],
    [-18, -20, -18, 31, 6, 4, -2, -12, 24],
    [27, 14, 4, -29, -3, 5, -29, 8, -12],
    [-15, -7, -23, 23, -9, -8, 6, 8, -12],
    [33, -23, -19, -4, -8, -7, 11, -12, 31],
    [-20, 19, -15, -30, 11, 32, 7, 14, -5],
    [-23, 18, -32, -2, -31, -7, 8, 24, 16],
    [32, -4, -10, -14, -6, -1, 0, 23, 23],
    [25, 0, -23, 22, 12, 28, -27, 15, 4],
    [-30, -13, -16, -3, -3, -32, -3, 27, -31],
    [22, 1, 26, 4, -2, -13, 26, 17, 14],
    [-9, -18, 3, -20, -27, -32, -11, 27, 13],
    [-17, 33, -7, 19, -32, 13, -31, -2, -24],
    [-31, 27, -31, -29, 15, 2, 29, -15, 33],
    [-18, -23, 15, 28, 0, 30, -4, 12, -32],
    [-3, 34, 27, -25, -18, 26, 1, 34, 26],
    [-21, -31, -10, -13, -30, -17, -12, -26, 31],
    [23, -31, -19, 21, -17, -10, 2, -23, 23],
    [-3, 6, 0, -3, -32, 0, -10, -25, 14],
    [-19, 9, 14, -27, 20, 15, -5, -27, 18],
    [11, -6, 24, 7, -17, 26, 20, -31, -25],
    [-25, 4, -16, 30, 33, 23, -4, -4, 23]
]
# End of data

# Import libraries
from cpmpy import *
import json

rows = len(input_matrix)
cols = len(input_matrix[0])

x = intvar(-100, 100, shape=(rows, cols), name="x")

# The domain is [-1,1], i.e. not including 0 (constrained later)
row_signs = intvar(-1, 1, shape=rows, name="row_signs")
col_signs = intvar(-1, 1, shape=cols, name="col_signs")

# for forcing rows and columns >= 0
row_sums = intvar(0, 300, shape=rows, name="row_sums")
col_sums = intvar(0, 300, shape=cols, name="col_sums")

# total sum: to be minimized
total_sum = intvar(0, 1000, name="total_sum")

model = Model(minimize=total_sum)

# constraints

# connect data + x + row_signs + col_signs
for i in range(rows):
    for j in range(cols):
        model += [x[i, j] == input_matrix[i][j] * row_signs[i] * col_signs[j]]

for i in range(rows):
    model += [row_signs[i] != 0]

for j in range(cols):
    model += [col_signs[j] != 0]

model += [total_sum == x.sum()]

# row sums
model += [[row_sums[i] == sum([x[i, j] for j in range(cols)])] for i in range(rows)]

# column sums
model += [[col_sums[j] == sum([x[i, j] for i in range(rows)])] for j in range(cols)]

# solve
model.solve()

# print
solution = {"row_signs": row_signs.value().tolist(), "col_signs": col_signs.value().tolist()}
print(json.dumps(solution, indent=4))
# End of CPMPy script
