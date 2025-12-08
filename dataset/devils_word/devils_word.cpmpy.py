#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/devils_word.py

"""
Given an array of integers, insert '+' or '-' operators before each integer in the array so that summing them up will
result in 666.

Print the array with the correct signs (result). For example, if the given array is [1, 2, 3], and the total is 4,
then the result array should be [-1, 2, 3].
"""

# Data
arr = [72, 229, 107, 97, 110, 32, 75, 106, 101, 108, 108, 101, 114, 115, 116, 114, 97, 110, 100]
total = 666
# End of data

# Import libraries
from cpmpy import *
import json

model = Model()

n = len(arr)
max_val = max(arr)

# variables
plus = boolvar(shape=n, name="plus")  # is the number arr[i] to be added
minus = boolvar(shape=n, name="minus")  # or is it to be subtracted?

# array with the number with correct sign
result = intvar(-max_val, max_val, shape=n, name="result")

# constraints
for i in range(n):
    # either plus or minus
    model += [plus[i] + minus[i] == 1]
    # calculate the result array
    model += [result[i] == arr[i] * plus[i] + (-arr[i]) * minus[i]]

# calculate the sum of the numbers in arr
model += [total == sum([result[i] for i in range(n)])]

# Solve the model
model.solve()

# Print the solution
solution = {"result": result.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
