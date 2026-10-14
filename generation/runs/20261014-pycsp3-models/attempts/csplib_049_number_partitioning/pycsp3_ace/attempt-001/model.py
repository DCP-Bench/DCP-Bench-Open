from pycsp3 import *

# Partition the numbers 1 to n into two sets A and B of the same size, with equal sums and equal
# sums of squares.
n = data.n
half = n // 2

# the members of set A and of set B; the names are lowercase, with the output names aliased below
a = VarArray(size=half, dom=range(1, n + 1))
b = VarArray(size=half, dom=range(1, n + 1))
A, B = a, b

# squares of the members, linked to the members by a table of (value, square) pairs
square_pairs = [(v, v * v) for v in range(1, n + 1)]
sq_a = VarArray(size=half, dom={v * v for v in range(1, n + 1)})
sq_b = VarArray(size=half, dom={v * v for v in range(1, n + 1)})

satisfy(
    # every number from 1 to n is in exactly one of the two sets
    AllDifferent(a + b),
    # the two sets have the same sum
    Sum(a) == Sum(b),
    # each member of A and of B is linked to its square
    [Table(scope=[a[i], sq_a[i]], supports=square_pairs) for i in range(half)],
    [Table(scope=[b[i], sq_b[i]], supports=square_pairs) for i in range(half)],
    # the two sets have the same sum of squares
    Sum(sq_a) == Sum(sq_b),
)
