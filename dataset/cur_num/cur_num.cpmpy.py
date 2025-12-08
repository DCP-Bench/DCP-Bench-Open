#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/cur_num.py
# Source description: Curious Numbers from "Amusements in Mathematics, Dudeney", number 114.

"""
The number 48 has this peculiarity, that if you add 1 to it the result
is a square number, and if you add 1 to its half, you also get a
square number.

Print another number with this peculiarity (peculiar) between 1 and 10000.
"""

# Import libraries
from cpmpy import *
import json

peculiar, a, b, c, d, e = intvar(1, 10000, shape=6)  # number, number + 1, its square root, number/2, number/2 + 1, its square root

model = Model([
    peculiar != 48,  # 48 is already known

    peculiar + 1 == a,  # if you add 1 to it
    a == b * b,  # the result is a square number

    peculiar == 2 * c,  # if you to its half
    c + 1 == d,  # add 1
    d == e * e,  # you also get a square number
])

# Solve the model
model.solve()

# Print the solution
solution = {"peculiar": peculiar.value()}
print(json.dumps(solution))
# End of CPMPy script
