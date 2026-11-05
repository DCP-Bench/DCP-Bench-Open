#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/divisible_by_1_through_9.py
# Source description: https://mindyourdecisions.com/blog/2016/04/10/find-the-10-digit-number-where-n-digits-are-divisible-by-n-sunday-puzzle/

# Import libraries
from cpmpy import *
import json

# Decision Variables
digits = intvar(0, 9, shape=10)  # The 10 digits
t = intvar(0, 10**10, shape=10)  # The 10 numbers formed by the first n digits

model = Model()

# Constraints
model += AllDifferent(digits)
for i in range(10):
    # find current number at position i
    cur_num = sum([digits[j] * (10 ** (i-j))   for j in range(i+1)])
    model += t[i] == cur_num

    # current number must be divisible by i+1
    model += t[i] % (i+1) == 0

# solve
model.solve()

# print
solution = {"digits": digits.value().tolist()}
print(json.dumps(solution, indent=4))
# End of CPMPy script
