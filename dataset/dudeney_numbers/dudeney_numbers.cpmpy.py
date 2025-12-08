#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/dudeney_numbers.py

"""
A Dudeney Number is a positive integer that is a perfect cube such
that the sum of its digits is equal to the cube root of the
number.

Print such a number (number) that is also larger than 1.
"""

# Data

# max number of digits
n = 6

# End of data

# Import libraries
from cpmpy import *
import json

# Decision Variables
number_digits = intvar(0, 9, shape=n)
number = intvar(0, 10 ** n - 1)
cube_root = intvar(1, 9 * n)

model = Model()

# Constraints
model += number == cube_root * cube_root * cube_root
model += cube_root == sum(number_digits)
model += number == sum([number_digits[i] * (10 ** (n - i - 1)) for i in range(n)])
model += number > 1

# solve
model.solve()

# print
solution = {"number": number.value()}
print(json.dumps(solution, indent=4))
# End of CPMPy script
