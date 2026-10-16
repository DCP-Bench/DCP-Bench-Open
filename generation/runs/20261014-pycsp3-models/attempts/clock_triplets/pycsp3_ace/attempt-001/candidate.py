from pycsp3 import *

# Clock with the numbers 1 to 12 placed on its 12 positions, read clockwise.
# The positions form a circle, so triplets of adjacent positions wrap around.

# x[i] is the number at clock position i
x = VarArray(size=12, dom=range(1, 13))

satisfy(
    # every number from 1 to 12 appears exactly once
    AllDifferent(x),

    # no triplet of adjacent numbers has a sum higher than 21
    [x[i] + x[(i + 1) % 12] + x[(i + 2) % 12] <= 21 for i in range(12)],
)
