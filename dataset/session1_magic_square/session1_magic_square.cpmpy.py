#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/magic_square.mzn

"""
A magic square is an n x n grid (n != 2) such that each cell contains a different integer from 1 to n^2 and the
sum of the integers in each row, column and diagonal is equal. Find a magic square for a given size n, knowing that the sum
of integers of each row, column and diagonal has to be equal to n(n^2+ 1)/2 (integer).

Print the magic square as a list of lists (square) of integers.
"""

# Data
n = 4  # size of the magic square
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
magic_sum = n * (n**2 + 1) // 2  # sum of each row, column and diagonal

# Decision Variables
square = intvar(1, n ** 2, shape=(n, n))  # the magic square

# Constraints
model = Model()

# All numbers in the magic square must be different
model += AllDifferent(square)

# The sum of the numbers in each row must be equal to the magic sum
for i in range(n):
    model += sum(square[i, :]) == magic_sum

# The sum of the numbers in each column must be equal to the magic sum
for j in range(n):
    model += sum(square[:, j]) == magic_sum

# The sum of the numbers in the main diagonal must be equal to the magic sum
model += sum(square[i, i] for i in range(n)) == magic_sum

# The sum of the numbers in the other diagonal must be equal to the magic sum
model += sum(square[i, n - 1 - i] for i in range(n)) == magic_sum

# Solve
model.solve()

# Print the solution
solution = {"square": square.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script