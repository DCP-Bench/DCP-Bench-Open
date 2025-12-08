#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/best_host.py
# Source description: http://www.informs.org/ORMS-Today/Public-Articles/February-Volume-38-Number-1/THE-PUZZLOR
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Hosting a dinner party requires several skills to pull off a successful
evening. One of your duties, aside from preparing dinner and selecting
the drinks, is to make sure your guests enjoy themselves.

Figure 1 shows a dinner table with six seats for your guests. Some
guests, however, do not get along with each other. If two guests who
do not get along are seated next to each other, it will create conflict
at dinner. As host, you must arrange the guests in a seating order
that minimizes conflict.

Andrew will only sit next to Dave and Frank;
Betty will only sit next to Cara and Erica;
Cara will only sit next to Betty and Frank;
Dave will only sit next to Andrew and Erica;
Erica will only sit next to Betty and Dave;
Frank will only sit next to Andrew and Cara.

[
  Figure 1 shows the following arrangement:

              Andrew
       Frank         Betty
       Erica         Cara
              Dave

]

In the example seating arrangement above, there are three conflicts
(Andrew and Betty, Cara and Dave, Erica and Frank).

Question:

What seating arrangement will minimize the conflict at dinner?

Print the list of guests (x) in the seating order, where 0 represents Andrew, 1 represents Betty, 2 represents Cara, 3 represents Dave, 4 represents Erica, and 5 represents Frank.
"""

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
