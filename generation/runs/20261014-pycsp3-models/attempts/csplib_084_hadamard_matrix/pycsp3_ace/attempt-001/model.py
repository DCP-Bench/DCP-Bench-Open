from pycsp3 import *

# Hadamard matrix via Legendre pairs: two sequences a and b of length l, with entries -1 or +1.
l = data.l
m = (l - 1) // 2

# a[i] and b[i] are the entries of the two sequences
a = VarArray(size=l, dom={-1, 1})
b = VarArray(size=l, dom={-1, 1})

satisfy(
    # the periodic autocorrelation of a plus that of b equals -2 at every shift s from 1 to m
    [Sum(a[i] * a[(i + s) % l] for i in range(l)) + Sum(b[i] * b[(i + s) % l] for i in range(l)) == -2
     for s in range(1, m + 1)],
    # the entries of a sum to 1
    Sum(a) == 1,
    # the entries of b sum to 1
    Sum(b) == 1,
)
