#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/kakuro.py

"""
The object of the puzzle is to insert a digit from 1 to 9 inclusive
into each white cell such that the sum of the numbers in each entry
matches the clue associated with it and that no digit is duplicated in
any entry. It is that lack of duplication that makes creating Kakuro
puzzles with unique solutions possible, and which means solving a Kakuro
puzzle involves investigating combinations more, compared to Sudoku in
which the focus is on permutations. There is an unwritten rule for
making Kakuro puzzles that each clue must have at least two numbers
that add up to it. This is because including one number is mathematically
trivial when solving Kakuro puzzles; one can simply disregard the
number entirely and subtract it from the clue it indicates.

Print the solution matrix (x) as a list of lists of integers ranging from 0 to 9; 0 represents a blank cell.
"""

# Data
# size of matrix
n = 7

# segments
#    [sum, [segments]]
# Note: 1-based
problem = [[16, [1, 1], [1, 2]], [24, [1, 5], [1, 6], [1, 7]],
           [17, [2, 1], [2, 2]], [29, [2, 4], [2, 5], [2, 6], [2, 7]],
           [35, [3, 1], [3, 2], [3, 3], [3, 4], [3, 5]], [7, [4, 2], [4, 3]],
           [8, [4, 5], [4, 6]], [16, [5, 3], [5, 4], [5, 5], [5, 6], [5, 7]],
           [21, [6, 1], [6, 2], [6, 3], [6, 4]], [5, [6, 6], [6, 7]],
           [6, [7, 1], [7, 2], [7, 3]], [3, [7, 6], [7, 7]],
           [23, [1, 1], [2, 1], [3, 1]], [30, [1, 2], [2, 2], [3, 2], [4, 2]],
           [27, [1, 5], [2, 5], [3, 5], [4, 5], [5, 5]], [12, [1, 6], [2, 6]],
           [16, [1, 7], [2, 7]], [17, [2, 4], [3, 4]],
           [15, [3, 3], [4, 3], [5, 3], [6, 3], [7, 3]],
           [12, [4, 6], [5, 6], [6, 6], [7, 6]], [7, [5, 4], [6, 4]],
           [7, [5, 7], [6, 7], [7, 7]], [11, [6, 1], [7, 1]],
           [10, [6, 2], [7, 2]]]
num_p = len(problem)

# The blanks
# Note: 1-based
blanks = [[1, 3], [1, 4], [2, 3], [3, 6], [3, 7], [4, 1], [4, 4], [4, 7],
          [5, 1], [5, 2], [6, 5], [7, 4], [7, 5]]
num_blanks = len(blanks)
# End of data

from cpmpy import *
import json

model = Model()

# Variables
x = intvar(0, 9, shape=(n, n), name="x")

# fill the blanks with 0
for i in range(num_blanks):
    model += x[blanks[i][0] - 1, blanks[i][1] - 1] == 0

for i in range(num_p):
    segment = problem[i][1::]
    res = problem[i][0]

    for j in segment:
        model += x[j[0] - 1, j[1] - 1] >= 1  # ensure that the values are positive
    # sum the numbers
    model += sum([x[j[0] - 1, j[1] - 1] for j in segment]) == res

    # all numbers in this segment must be distinct
    model += AllDifferent([x[p[0] - 1, p[1] - 1] for p in segment])

model.solve()

# Output
solution = {
    'x': x.value().tolist()
}
print(json.dumps(solution, indent=4))
# End of CPMPy script
