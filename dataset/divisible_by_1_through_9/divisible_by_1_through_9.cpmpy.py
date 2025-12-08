#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/divisible_by_1_through_9.py
# Source description: https://mindyourdecisions.com/blog/2016/04/10/find-the-10-digit-number-where-n-digits-are-divisible-by-n-sunday-puzzle/

"""
Find a 10 digit number that uses each of the digits 0 to 9 exactly once and
where the number formed by the first n digits of the number is divisible by n.

You should read the digits of the number from left to right. For example, in the
number abcd, you need the number a to be divisible by 1, the number ab to be
divisible by 2, the number abc to be divisible by 3, and the entire number abcd
to be divisible by 4.

Print the number (number).
"""

# Import libraries
from cpmpy import *
import json

# Decision Variables
x = intvar(0, 9, shape=10)  # The 10 digits
t = intvar(0, 10**10, shape=10)  # The 10 numbers formed by the first n digits
number = t[9]

model = Model()

# Constraints
model += AllDifferent(x)
for i in range(10):
    # find current number at position i
    cur_num = sum([x[j] * (10 ** (i-j))   for j in range(i+1)])
    model += t[i] == cur_num

    # current number must be divisible by i+1
    model += t[i] % (i+1) == 0

# solve
model.solve()

# print
solution = {"number": number.value()}
print(json.dumps(solution, indent=4))
# End of CPMPy script
