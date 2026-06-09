#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/isbn.py

"""
ISBN-13 Validation and Check Digit Calculation.

Problem:
An ISBN-13 (International Standard Book Number) is a 13-digit number where the last digit is a check digit
calculated from the first 12 digits.  The check digit is calculated as follows:

1.  Multiply the first 12 digits alternately by 1 and 3 (starting with 1).
2.  Sum the products.
3.  The check digit is (10 - (sum % 10)) % 10.

Given a list of 13 integers representing an ISBN-13, where -1 represents an unknown digit,
find the values of the unknown digits such that the resulting number is a valid ISBN-13.
An ISBN-13 must start with 978 or 979.

Print the complete valid isbn (isbn) as a list of integers.
"""

# Data
isbn_init = [9, 7, 8, 3, 3, 1, 9, 2, 5, 8, 8, 1, -1]  # Example: Find the missing digit (-1)
# End of data

from cpmpy import *
import json

# Variables
n = 13
isbn = intvar(0, 9, shape=n, name="isbn")

# Constraints
model = Model()

# Set known digits (or keep unknowns as -1 is not a valid digit)
for i in range(n):
    if isbn_init[i] != -1:
        model += isbn[i] == isbn_init[i]

# ISBN-13 prefixes
model += isbn[0] == 9
model += isbn[1] == 7
model += (isbn[2] == 8) | (isbn[2] == 9)

# Check digit calculation
check_sum = sum(isbn[i] * (1 if i % 2 == 0 else 3) for i in range(n - 1))
model += isbn[n - 1] == (10 - (check_sum % 10)) % 10

model.solve()

solution = {
    'isbn': isbn.value().tolist()
}
print(json.dumps(solution, indent=4))
# End of CPMPy script
