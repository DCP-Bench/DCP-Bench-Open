#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/just_forgotten.py
# Misc: Enigma 1517 Bob Walker, New Scientist magazine, October 25, 2008.

"""
Joe was furious when he forgot one of his bank account numbers.
He remembered that it had all the digits from 0 to n-1 in some order,
so he tried a number of sets without success.

When Joe finally remembered his account number, he realised that
in each set just a specific number of the digits were in their correct position
and that, if one knew that, it was possible to work out his
account number.

Print Joe's account number (x) as a list of n integers.
"""

# Data
sets = [
    [9, 4, 6, 2, 1, 5, 7, 8, 3, 0],
    [8, 6, 0, 4, 3, 9, 1, 2, 5, 7],
    [1, 6, 4, 0, 2, 9, 7, 8, 5, 3],
    [6, 8, 2, 4, 3, 1, 9, 0, 7, 5]
]
num_correct_digits = 4
# End of data

# Import libraries
from cpmpy import *
import json

n = len(sets[0])
x = intvar(0, n-1, shape=n, name="x")

# Constraints
model = Model()

# All digits from 0 to n-1 must be used
model += AllDifferent(x)

for s in sets:
    model += [sum([x[i] == s[i] for i in range(n)]) == num_correct_digits]

# Solve
model.solve()

# Output
solution = {
    'x': x.value().tolist()
}
print(json.dumps(solution, indent=4))
# End of CPMPy script
