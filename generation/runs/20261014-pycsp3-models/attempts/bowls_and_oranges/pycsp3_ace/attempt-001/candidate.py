from itertools import combinations

from pycsp3 import *

# Bowls are numbered 1 to n in a line, one meter apart. We place m oranges,
# at most one per bowl, so that no three oranges have equal spacing.
n = data.n
m = data.m

# x[k] is the bowl of the k-th orange, in ascending order
x = VarArray(size=m, dom=range(1, n + 1))

satisfy(
    # the oranges are in ascending order of bowl and each bowl holds at most one orange
    Increasing(x, strict=True),
    # no three oranges A, B, C with the distance from A to B equal to the distance from B to C
    [x[a] + x[c] != 2 * x[b] for a, b, c in combinations(range(m), 3)],
)
