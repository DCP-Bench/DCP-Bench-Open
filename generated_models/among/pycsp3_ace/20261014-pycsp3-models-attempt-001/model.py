# Among: choose x[0..n-1] with values in 0..7 so that exactly m entries of x take a value from the set v.
from pycsp3 import *

n = data.n
m = data.m
v = data.v

# x[i] is the value chosen for position i, in 0..7
x = VarArray(size=n, dom=range(8))
# b[i] = 1 if x[i] takes one of the values in v, else 0
b = VarArray(size=n, dom={0, 1})

satisfy(
    # each position is linked to the set of values v: b[i] is 1 exactly when x[i] is in v
    [(x[i], b[i]) in [(a, 1) for a in v] + [(a, 0) for a in range(8) if a not in v] for i in range(n)],
    # exactly m values in x must take one of the values in v
    Sum(b) == m,
)
