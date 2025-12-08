#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/bank_card.mzn

"""
My bank card has a 4 digit pin, abcd. I use the following facts to help me remember it:

- no two digits are the same
- the 2-digit number cd is 3 times the 2-digit number ab
- the 2-digit number da is 2 times the 2-digit number bc

Print the PIN (a, b, c, d).
"""

# Import libraries
from cpmpy import *
import json

# Decision Variables
a, b, c, d = intvar(0, 9, shape=4)  # a, b, c, d are the four digits of the PIN

# Constraints
model = Model()

model += AllDifferent([a, b, c, d])  # no two digits are the same
model += 10 * c + d == 3 * (10 * a + b)  # cd is 3 times ab
model += 10 * d + a == 2 * (10 * b + c)  # da is 2 times bc

# Solve
model.solve()

# Print the solution
solution = {"a": a.value(), "b": b.value(), "c": c.value(), "d": d.value()}
print(json.dumps(solution))
# End of CPMPy script
