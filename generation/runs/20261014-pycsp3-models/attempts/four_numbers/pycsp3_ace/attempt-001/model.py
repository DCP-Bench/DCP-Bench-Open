from pycsp3 import *

# Find three integers between 1 and 10 such that every given number is the sum of a
# non-empty subset of the three integers.

numbers = data.numbers

# x holds the three integers
x = VarArray(size=3, dom=range(1, 11))

satisfy(
    # each given number is one of the seven non-empty subset sums of x
    [Or(
        v == x[0], v == x[1], v == x[2],
        v == x[0] + x[1], v == x[0] + x[2], v == x[1] + x[2],
        v == x[0] + x[1] + x[2],
    ) for v in numbers],
)
