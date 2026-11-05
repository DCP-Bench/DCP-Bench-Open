#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/best_host.py
# Source description: http://www.informs.org/ORMS-Today/Public-Articles/February-Volume-38-Number-1/THE-PUZZLOR
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

# Import libraries
from cpmpy import *
import json


def member_of(x, val):
    """
    member_of(x, val)

    Ensures that the value `val` is in the array `x`.
    """
    n = len(x)
    # cc = intvar(0,n)
    # constraints = [count(x, val, cc), cc >  0]
    constraints = [sum([x[i] == val for i in range(n)]) > 0]
    return constraints


model = Model()

n = 6

Andrew = 0
Betty = 1
Cara = 2
Dave = 3
Erica = 4
Frank = 5

prefs = cpm_array([
    [Dave, Frank],  # Andrew
    [Cara, Erica],  # Betty
    [Betty, Frank],  # Cara
    [Andrew, Erica],  # Dave
    [Betty, Dave],  # Erica
    [Andrew, Cara]  # Frank
])

# declare variables
x = intvar(0, n - 1, shape=n, name="x")

#
# constraints
#
model += (AllDifferent(x))

# symmetry breaking
# <SYMMETRY_BREAKING_CONSTRAINT_START>
# model += (x[0] == Andrew)
# <SYMMETRY_BREAKRY_CONSTRAINT_END>

for i in range(n):
    # This don't work:
    # TypeError: object of type 'Element' has no len()
    # model += [member_of(prefs[x[i]], x[(i-1) % n])]
    # model += [member_of(prefs[x[i]], x[(i+1) % n])]

    # It works if we expand the array:
    model += [member_of([prefs[x[i], j] for j in range(2)], x[(i - 1) % n])]
    model += [member_of([prefs[x[i], j] for j in range(2)], x[(i + 1) % n])]

    # Another approach that works
    # model += [sum([prefs[x[i],j] == x[(i-1) % n] for j in range(2)])>0]
    # model += [sum([prefs[x[i],j] == x[(i+1) % n] for j in range(2)])>0]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
