#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob024_langford.py
# Source description: https://www.csplib.org/Problems/prob024/

"""
Consider two sets of the numbers from 1 to k. The problem is to arrange the 2k numbers in the two sets into a
single sequence in which the two 1’s appear one number apart, the two 2’s appear two numbers apart, ..., and the two k's appear k numbers apart.

Print the solution sequence (sol) as a list of 2k integers from 1 to k.
"""

# Data
k = 12
# End of data

# Import libraries
import json
from cpmpy import *


def langford(k):
    model = Model()

    if not (k % 4 == 0 or k % 4 == 3):
        print("There is no solution for K unless K mod 4 == 0 or K mod 4 == 3")
        return None, None

    # Variables
    position = intvar(0, 2 * k - 1, shape=2 * k, name="position")
    sol = intvar(1, k, shape=2 * k, name="sol")

    # Constraints
    model += [AllDifferent(position)]

    for i in range(1, k + 1):
        model += [position[i + k - 1] == position[i - 1] + i + 1]
        model += [i == sol[position[i - 1]]]
        model += [i == sol[position[k + i - 1]]]

    # Symmetry breaking
    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # model += [sol[0] < sol[2 * k - 1]]
    # <SYMMETRY_BREAKING_CONSTRAINT_END>

    return model, (position, sol)


# Example usage
model, (position, sol) = langford(k)

model.solve()

# Print
solution = {
    "sol": sol.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script